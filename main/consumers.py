import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import MessageTchat  # Note le changement vers ton nouveau modèle
from django.contrib.auth.models import User
from .models import MessageTchat  # Assurez-vous que le modèle de message existe
from django.db.models import Q

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Vérifier si l'utilisateur est authentifié
        if self.scope['user'].is_authenticated:
            self.group_name = 'chat'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

            # Charger les messages du chat général
            messages = await self.get_messages()
            for message in messages:
                await self.send(text_data=json.dumps({
                    'message': f'{message["user__username"]}: {message["content"]}',
                    'timestamp': message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')  # Inclure le timestamp
                }))
        else:
            # Refuser la connexion si l'utilisateur n'est pas connecté
            await self.close()


    async def disconnect(self, close_code):
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        if self.scope['user'].is_authenticated:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            user = self.scope['user']
            # Sauvegarder le message dans la base de données
            new_message = await self.save_message(user, message)

            # Envoyer le message à tous les membres du groupe avec le timestamp
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': f'{user.username}: {message}',  # Envoyer avec l'utilisateur
                    'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Inclure le timestamp
                }
            )




    async def chat_message(self, event):
        message = event['message']
        timestamp = event['timestamp']  # Ajouter le timestamp

        # Envoyer le message au WebSocket avec le timestamp
        await self.send(text_data=json.dumps({
            'message': message,
            'timestamp': timestamp  # Inclure le timestamp
        }))


    @database_sync_to_async
    def get_messages(self):
        return list(
            MessageTchat.objects.filter(recipient__isnull=True)
            .order_by('-timestamp')
            .values('user__username', 'content', 'timestamp')[:50][::-1]  # Renverser la liste
        )

    @database_sync_to_async
    def save_message(self, user, content):
        return MessageTchat.objects.create(user=user, content=content, recipient=None)



class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()

        users = sorted([self.user.username, self.username])
        self.group_name = f'private_chat_{"_".join(users)}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # Charger les messages précédents et les envoyer au client
        messages = await self.get_messages()
        for message in messages:
            await self.send(text_data=json.dumps({
                'message': f'{message["user__username"]}: {message["content"]}',
                'timestamp': message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')  # Inclure et formater le timestamp
            }))


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Enregistrer le message dans la base de données uniquement s'il y a un destinataire
        if self.username and self.user.is_authenticated:
            new_message = await self.save_message(self.user, self.username, message)

            # Envoyer le message au groupe de chat privé avec le timestamp
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': f'{self.user.username}: {message}',
                    'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')  # Formater le timestamp
                }
            )
        else:
            await self.close()

    async def chat_message(self, event):
        message = event['message']
        timestamp = event['timestamp']  # Ajoutez le timestamp ici

        # Envoyer le message au WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'timestamp': timestamp  # Inclure le timestamp dans les données envoyées
        }))

    @database_sync_to_async
    def save_message(self, sender, recipient_username, content):
        try:
            # Vérifier que le destinataire existe
            recipient = User.objects.get(username=recipient_username)
        except User.DoesNotExist:
            recipient = None

        # Créer et retourner le message enregistré dans la base de données
        new_message = MessageTchat.objects.create(user=sender, recipient=recipient, content=content)

        # Retourner le message avec son timestamp
        return new_message

    @database_sync_to_async
    def get_messages(self):
        try:
            recipient = User.objects.get(username=self.username)
        except User.DoesNotExist:
            return []
        messages = MessageTchat.objects.filter(
            Q(user=self.user, recipient=recipient) |
            Q(user=recipient, recipient=self.user)
        ).order_by('timestamp')
        
        # Inclure le timestamp dans les valeurs retournées
        return list(messages.values('user__username', 'content', 'timestamp'))
