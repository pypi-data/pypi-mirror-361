'''
MIT License

Copyright (c) 2025 Fatih Kuloglu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import asyncio
import aiohttp
import json




from .utils import MISSING
from typing import Any, Dict, List, Literal, Union, Optional
from urllib.parse import quote
from loguru import logger

async def json_or_text(response: aiohttp.ClientResponse) -> Union[Dict[str, Any], str]:
    text = await response.text(encoding='utf-8')
    try:
        if response.headers['content-type'] == 'application/json':
            return json.loads(text)
    except KeyError:
        pass

    return text

class Route:
    '''
        Represents an API route with a method and path, used to build full request URLs
        for the Teamly API.

        Example:
            Route("GET", "/channels/{channel_id}", channel_id="1234")
            → https://api.teamly.one/api/v1/channels/1234

        Attributes:
            BASE_URL (str): The base URL for all API requests.
            method (str): The HTTP method (e.g., "GET", "POST").
            path (str): The API path, possibly containing placeholders.
            url (str): The fully constructed request URL.
    '''

    BASE_URL = "https://api.teamly.one/api/v1"

    def __init__(self, method:str, path: str, **params: Any) -> None:
        self.method = method
        self.path = path

        url = self.BASE_URL + self.path
        if params:
            url = url.format_map({
                k: quote(v, safe='') if isinstance(v, str) else v
                for k, v in params.items()
            })
        self.url: str = url

class HTTPClient:

    def __init__(self,loop: asyncio.AbstractEventLoop) -> None:
        self._session: aiohttp.ClientSession = MISSING
        self.token = None
        self.loop: asyncio.AbstractEventLoop = loop

    async def static_login(self, token: str):
        logger.debug("static logging...")

        self.token = token
        self._session = aiohttp.ClientSession()

        try:
            data = await self.get_loggedIn_user
        except Exception as e:
            logger.debug("Exception error: {}",e)
        else:
            return data

    async def close(self):
        logger.debug("closing client session...")
        await self._session.close()

    async def ws_connect(self) -> aiohttp.ClientWebSocketResponse:
        logger.debug("creating ws connect...")

        kwargs = {
            "timeout": 30,
            "max_msg_size": 0,
            "headers": {
                "Authorization": f'Bot {self.token}'
            }
        }

        return await self._session.ws_connect(url="wss://api.teamly.one/api/v1/ws", **kwargs)

    async def request(self, route: Route, **kwargs) -> Any:
        method = route.method
        url = route.url

        #creating headers
        headers = {}

        if self.token is not None:
            headers["Authorization"] = f'Bot {self.token}'

        if 'json' in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs['data'] = json.dumps(kwargs.pop('json'))

        kwargs["headers"] = headers

        data: Optional[Union[Dict[str,Any], str]] = None
        try:
            async with self._session.request(method, url, **kwargs) as response:
                logger.debug("Sending request {!r} {} with {}", method, url, kwargs)

                data = await json_or_text(response)

                status = response.status
                if 200 <= status < 300:
                    logger.debug("Request successful with status {}", status)
                elif 400 <= status < 500:
                    logger.warning("Client error with status {}", status)
                elif status >= 500:
                    logger.error("Server error with status {}", status)
                else:
                    logger.debug("Received status {}", status)

                return data
        except Exception as e:
            logger.error("Request failed: {}", e)
            raise


    #Core Resources

    #Channels
    async def get_channels(self, teamId: str):
        return await self.request(Route("GET","/teams/{teamId}/channels", teamId=teamId))

    async def create_channel(self, teamId: str, payload: Dict[str,Any]):
        r = Route("PUT", "/teams/{teamId}/channels", teamId=teamId)
        return await self.request(r,json=payload)

    async def delete_channel(self, teamId: str, channelId: str):
        r = Route("DELETE","/teams/{teamId}/channels/{channelId}", teamId=teamId, channelId=channelId)
        return await self.request(r)

    async def duplicate_channel(self, teamId: str, channelId: str):
        r = Route("POST","/teams/{teamId}/channels/{channelId}/clone", teamId=teamId, channelId=channelId)
        return await self.request(r)

    async def update_channel_priorities(self, teamId: str, channelId: str, payload: Dict[str, Any]):
        r = Route("PUT","/teams/{teamId}/channelspriority", teamId=teamId)
        return await self.request(r,json=payload)

    async def get_channel_by_Id(self, teamId: str, channelId: str):
        r = Route("GET","/teams/{teamId}/channels/{channelId}", teamId=teamId, channelId=channelId)
        return await self.request(r)




    async def update_channel(self, teamId: str, channelId: str, payload: Dict[str, Any]):
        r = Route("PATCH","/teams/{teamId}/channels/{channelId}", teamId=teamId, channelId=channelId)
        return await self.request(r, json=payload)

    async def update_channel_permissions(self, teamId: str, channelId: str, roleId: str, allow: int, deny: int):
        payload = {"allow": allow, "deny": deny}
        r = Route("POST","/teams/{teamId}/channels/{channelId}/permissions/role/{roleId}", teamId=teamId, channelId=channelId, roleId=roleId)
        return await self.request(r,json=payload)



    #Message
    async def create_message(self, channelId: str, payload: Dict[str,Any]):
        r = Route("POST","/channels/{channelId}/messages", channelId=channelId)
        return await self.request(r,json=payload)

    async def delete_message(self, channelId: str, messageId: str):
        r = Route("DELETE","/channels/{channelId}/messages/{messageId}",messageId=messageId, channelId=channelId)
        return await self.request(r)

    async def get_channel_messages(self, channelId: str, offset: str = '0', limit: str = '15'):
        r = Route("GET","/channels/{channelId}/messages" + f"?offset={offset}&limit={limit}", channelId=channelId)
        return await self.request(r)

    async def update_channel_message(self, channelId: str, messageId: str, payload: Dict[str, Any]):
        r = Route("PATCH","/channels/{channelId}/messages/{messageId}", channelId=channelId, messageId=messageId)
        return await self.request(r,json=payload)

    async def react_to_message(self, channelId: str, messageId: str, emojiId: str):
        r = Route("POST","/channels/{channelId}/messages/{messageId}/reactions/{emojiId}", channelId=channelId, messageId=messageId, emojiId=emojiId)
        return await self.request(r)

    async def delete_reaction_from_message(self, channelId: str, messageId: str, emojiId: str):
        r = Route("DELETE","/channels/{channelId}/messages/{messageId}/reactions/{emojiId}", channelId=channelId, messageId=messageId, emojiId=emojiId)
        return await self.request(r)

    async def get_channel_message_by_id(self, channelId: str, messageId: str):
        r = Route("GET","/channels/{channelId}/messages/{messageId}", channelId=channelId, messageId=messageId)
        return await self.request(r)


    ### Teams ###

    #Members
    async def add_role_to_member(self, teamId: str, userId: str, roleId: str):
        r = Route("POST","/teams/{teamId}/members/{userId}/roles/{roleId}", teamId=teamId, userId=userId, roleId=roleId)
        return await self.request(r)

    async def remove_role_from_member(self, teamId: str, userId: str, roleId: str):
        r = Route("DELETE","/teams/{teamId}/members/{userId}/roles/{roleId}", teamId=teamId, userId=userId, roleId=roleId)
        return await self.request(r)

    async def kick_member(self, teamId: str, userId: str):
        r = Route("DELETE","/teams/{teamId}/members/{userId}", teamId=teamId, userId=userId)
        return await self.request(r)

    async def get_member(self, teamId: str, userId):
        r = Route("GET","/teams/{teamId}/members/{userId}", teamId=teamId, userId=userId)
        return await self.request(r)

    #Bans
    async def get_banned_user(self, teamId: str, limit: str = 10):
        r = Route("GET","/teams/{teamId}/bans" + f"?limit={limit}", teamId=teamId)
        return await self.request(r)

    async def unban(self, teamId: str, userId: str):
        r = Route("DELETE","/teams/{teamId}/members/{userId}/ban", teamId=teamId, userId=userId)
        return await self.request(r)

    async def ban(self, teamId: str, userId: str, reason: str):
        payload = {"reason": reason}
        r = Route("POST","/teams/{teamId}/members/{userId}/ban", teamId=teamId, userId=userId)
        return await self.request(r, json=payload)



    async def get_team(self, teamId: str):
        r = Route("GET","/teams/{teamId}/details", teamId=teamId)
        return await self.request(r)

    #https://docs.teamly.one/update-a-team-12817978e0
    async def update_team(self, teamId: str,*, payload: Dict[str, Any]):
        r = Route("POST","/teams/{teamId}", teamId=teamId)
        return await self.request(r, json=payload)



    #Roles
    #https://docs.teamly.one/create-a-role-for-team-12817984e0
    async def create_role(self, teamId: str, payload: Dict[str, Any]):
        r = Route("POST","/teams/{teamId}/roles", teamId=teamId)
        return await self.request(r, json=payload)

    async def get_role(self, teamId: str):
        r = Route("GET","/teams/{teamId}/roles", teamId=teamId)
        return await self.request(r)

    async def delete_role(self, teamId: str, roleId: str):
        r = Route("DELETE","/teams/{teamId}/roles/{roleId}", teamId=teamId, roleId=roleId)
        return await self.request(r)

    async def clone_role(self, teamId: str, roleId: str):
        r = Route("POST","/teams/{teamId}/roles/{roleId}/clone", teamId=teamId, roleId=roleId)
        return await self.request(r)

    async def update_role_priorities(self, teamId: str, payload: Dict[None,List[str]]):
        r = Route("PATCH","/teams/{teamId}/roles-priority", teamId=teamId)
        return await self.request(r, json=payload)

    async def update_role(self, teamId: str, roleId: str, payload: Dict[str, Any]):
        r = Route("POST","/teams/{teamId}/roles/{roleId}", teamId=teamId, roleId=roleId)
        return await self.request(r, json=payload)



    #User
    async def get_user(self, userId: str):
        return await self.request(Route("GET","/users/{userId}", userId=userId))

    @property
    async def get_loggedIn_user(self):
        return await self.request(Route("GET","/me"))



    #Todos
    async def get_todo_items(self, channelId: str):
        r = Route("GET","/channels/{channelId}/todo/list", channelId=channelId)
        return await self.request(r)

    async def create_todo_item(self, channelId: str, content: str):
        payload = {"content": content}
        r = Route("POST","/channels/{channelId}/todo/item", channelId=channelId)
        return await self.request(r, json=payload)

    async def delete_todo_item(self, channelId: str, todoId: str):
        r = Route("DELTE","/channels/{channelId}/todo/item/{todoId}", channelId=channelId, todoId=todoId)
        return await self.request(r)

    async def clone_todo_item(self, channelId: str, todoId: str):
        r = Route("POST","/channels/{channelId}/todo/item/{todoId}/clone", channelId=channelId, todoId=todoId)
        return await self.request(r)

    async def update_todo_item(self, channelId: str, todoId: str, content: str, completed: bool = False):
        payload = {"content": content, "changeCompleted": completed}
        r = Route("PUT","/channels/{channelId}/todo/item/{todoId}", channelId=channelId, todoId=todoId)
        return await self.request(r, json=payload)




    #Direct Message
    async def create_direct_message(self, payload: Dict[str,List[Dict[str,str]]]):
        r = Route("POST","/me/chats")
        return await self.request(r, json=payload)



    #Application
    async def get_application_submissions(self, teamId: str):
        r = Route("GET","/teams/{teamId}/applications", teamId=teamId)
        return await self.request(r)

    async def update_application_status(
        self,
        teamId: str,
        applicationId: str,
        status: Literal["accepted","rejected"]
    ):
        payload = {"status": status}
        r = Route("POST","/teams/{teamId}/applications/{applicationId}", teamId=teamId, applicationId=applicationId)
        return await self.request(r,json=payload)

    async def update_team_application_status(self, teamId: str, enable: bool):
        payload = {"enable": enable}
        r = Route("POST","/teams/{teamId}/applications/status", teamId=teamId)
        return await self.request(r, json=payload)

    async def update_team_application_questions(self, teamId: str, payload: Dict[str, Any]):
        r = Route("PATCH","/teams/{teamId}/applications", teamId=teamId)
        return await self.request(r, json=payload)

    async def get_application_by_id(self, teamId: str, applicationId: str):
        r = Route("GET","/teams/{teamId}/applications/{applicationId}", teamId=teamId, applicationId=applicationId)
        return await self.request(r)




    #Reactions
    async def get_team_custom_reactions(self, teamId: str):
        r = Route("GET","/teams/{teamId}/reactions", teamId=teamId)
        return await self.request(r)

    async def create_new_custom_reaction_for_team(self, teamId: str, name: str, payload: aiohttp.FormData):
        r = Route("POST","/teams/{teamId}/reactions", teamId=teamId)
        return await self.request(r, data=payload)

    async def update_custom_reaction(self, teamId: str, reactionId: str, name: str):
        payload = {"name": name}
        r = Route("PUT","/teams/{teamId}/reactions/{reactionId}", teamId=teamId, reactionId=reactionId)
        return await self.request(r, json=payload)

    async def delete_custom_reaction(self, teamId: str, reactionId: str):
        r = Route("DELETE","/teams/{teamId}/reactions/{reactionId}", teamId=teamId, reactionId=reactionId)
        return await self.request(r)



    #Attachments
    async def upload_attachment(self, payload: aiohttp.FormData):
        r = Route("POST","/upload")
        return await self.request(r, data=payload)




    #Voice
    async def get_credential_for_join_voice_channel(self, teamId: str, channelId, token: str = None):
        url = "/teams/{teamId}/channels/{channelId}/join"
        if token is not None:
            url += f"?token={token}"

        r = Route("GET",url, teamId=teamId, channelId=channelId)
        return await self.request(r)

    async def update_your_voice_metadata(
        self,
        teamId: str,
        channelId: str,
        isMuted: bool = True,
        isDeafened: bool = True
    ):
        payload = {"isMuted": isMuted, "isDeafened": isDeafened}
        r = Route("POST","/teams/{teamId}/channels/{channelId}/metadata", teamId=teamId, channelId=channelId)
        return await self.request(r,json=payload)

    async def leave_voice_channel(self, teamId: str, channelId: str):
        r = Route("GET","/teams/{teamId}/channels/{channelId}/leave", teamId=teamId, channelId=channelId)
        return await self.request(r)

    async def move_member(self, teamId: str, channelId: str, userId: str, fromChannelId: str):
        payload = {
            "userId": userId,
            "fromChannelId": fromChannelId
        }
        r = Route("POST","/teams/{teamId}/channels/{channelId}/move", teamId=teamId, channelId=channelId)
        return await self.request(r, json=payload)

    async def disconnect_member_from_voice(self, teamId: str, channelId: str, userId: str):
        r = Route("POST","/teams/{teamId}/channels/{channelId}/participants/{userId}/disconnect", teamId=teamId, channelId=channelId, userId=userId)
        return await self.request(r)




    #Webhooks
    async def create_webhook_message(self, webhookId: str, webhookToken: str, payload: Dict[str, Any]):
        r = Route("POST","/webhooks/{webhookId}/{webhookToken}", webhookId=webhookId, webhookToken=webhookToken)
        return await self.request(r, json=payload)

    async def webhook_for_github(self, webhookId: str, webhookToken: str):
        r = Route("POST","/webhooks/{webhookId}/{webhookToken}/github", webhookId=webhookId, webhookToken=webhookToken)
        return await self.request(r)



    #Blog
    async def get_blog_post(self, teamId: str):
        r = Route("GET","/teams/{teamId}/blogs", teamId=teamId)
        return await self.request(r)

    async def create_blog_post(self, teamId: str, payload: Dict[str, Any]):
        r = Route("POST","/teams/{teamId}/blogs", teamId=teamId)
        return await self.request(r, json=payload)

    async def delete_blog_post(self, teamId: str, blogId: str):
        r = Route("DELETE","/teams/{teamId}/blogs/{blogId}", teamId=teamId, blogId=blogId)
        return await self.request(r)



    #Category
    async def create_category(self, teamId: str, name: str):
        payload = {"name": name}
        r = Route("POST","/teams/{teamId}/categories", teamId=teamId)
        return await self.request(r,json=payload)

    async def update_category(self, teamId: str, categoryId: str, name: str):
        payload = {"name": name}
        r = Route("PUT","/teams/{teamId}/categories/{categoryId}", teamId=teamId, categoryId=categoryId)
        return await self.request(r,json=payload)

    async def update_category_role_permission(
        self,
        teamId: str,
        categoryId: str,
        roleId: str,
        allow: int = 0,
        deny: int = 0
    ):
        payload = {
            "allow": allow,
            "deny": deny
        }
        r = Route("POST","/teams/{teamId}/categories/{categoryId}/permissions/role/{roleId}", teamId=teamId, categoryId=categoryId, roleId=roleId)
        return await self.request(r,json=payload)

    async def delete_category(self, teamId: str, categoryId: str):
        r = Route("DELETE","/teams/{teamId}/categories/{categoryId}", teamId=teamId, categoryId=categoryId)
        return await self.request(r)

    async def add_channel_to_category(self, teamId: str, categoryId: str, channelId: str):
        r = Route("POST","/teams/{teamId}/categories/{categoryId}/channels/{channelId}", teamId=teamId, categoryId=categoryId, channelId=channelId)
        return await self.request(r)

    async def delete_channel_from_category(self, teamId: str, categoryId: str, channelId: str):
        r = Route("DELETE","/teams/{teamId}/categories/{categoryId}/channels/{channelId}", teamId=teamId, categoryId=categoryId, channelId=channelId)
        return await self.request(r)

    async def set_channel_priority_of_category(self, teamId: str, categoryId: str, payload: Dict[str, List[str]]):
        r = Route("POST","/teams/{teamId}/categories/{categoryId}/channels-priority", teamId=teamId, categoryId=categoryId)
        return await self.request(r, json=payload)

    async def set_team_category_priority(self, teamId: str, payload: Dict[str,List[str]]):
        r = Route("POST","/teams/{teamId}/categories-priority", teamId=teamId)
        return await self.request(r, json=payload)




    #Announcements
    async def get_announcments(self, channelId: str):
        r = Route("GET","/channels/{channelId}/announcements", channelId=channelId)
        return await self.request(r)

    async def create_announcment(self, channelId: str, payload: Dict[str, Any]):
        r = Route("POST","/channels/{channelId}/announcements", channelId=channelId)
        return await self.request(r, json=payload)

    async def delete_announcement(self, channelId: str, announcementId: str):
        r = Route("DELETE","/channels/{channelId}/announcements/{announcementId}", channelId=channelId, announcementId=announcementId)
        return await self.request(r)
