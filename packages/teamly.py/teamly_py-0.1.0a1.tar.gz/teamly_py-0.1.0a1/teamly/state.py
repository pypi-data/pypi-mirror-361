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


import inspect
import json

from .http import HTTPClient
from typing import Dict, Callable, Any

class ConnectionState:

    def __init__(self, dispatch: Callable[...,Any],http: HTTPClient) -> None:
        self.http: HTTPClient = http
        self.dispatch: Callable[...,Any] = dispatch

        self.parsers: Dict[str, Callable[[Any], None]]
        self.parsers = parsers = {}
        for attr, func in inspect.getmembers(self):
            if attr.startswith('parse_'):
                parsers[attr[6:].upper()] = func



    def parse_ready(self, data: Any):
        self.dispatch("ready")
        print(json.dumps(data,indent=4, ensure_ascii=False))



    def parse_channel_created(self, data: Dict[str,Any]):
        self.dispatch('channel_create')
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_channel_deleted(self, data: Any):
        self.dispatch('channel_delete')
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_channel_updated(self, data: Any):
        self.dispatch('channel_update')
        print(json.dumps(data,indent=4, ensure_ascii=False))



    def parse_message_send(self, data: Any):
        self.dispatch("message")

    def parse_message_updated(self, data: Any):
        self.dispatch("message_updated")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_message_deleted(self, data: Any):
        self.dispatch("message_delete")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_message_reaction_added(self, data: Any):
        self.dispatch("message_reaction")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_message_reaction_removed(self, data: Any):
        self.dispatch("message_reaction_removed")
        print(json.dumps(data,indent=4, ensure_ascii=False))



    def parse_presence_update(self, data: Any):
        self.dispatch("presence_update")
        print(json.dumps(data,indent=4, ensure_ascii=False))



    def parse_team_role_created(self, data: Any):
        self.dispatch("team_role")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_team_role_deleted(self, data: Any):
        self.dispatch("team_role_deleted")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_team_roles_updated(self, data: Any):
        self.dispatch("team_roles_updated")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_team_updated(self, data: Any):
        self.dispatch("team_updated")
        print(json.dumps(data,indent=4, ensure_ascii=False))



    def parse_todo_item_created(self, data: Any):
        self.dispatch("todo_item")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_todo_item_deleted(self, data: Any):
        self.dispatch("todo_item_deleted")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_todo_item_updated(self, data: Any):
        self.dispatch("todo_item_updated")
        print(json.dumps(data,indent=4, ensure_ascii=False))




    def parse_user_joined_team(self, data: Any):
        self.dispatch("user_joined_team")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_user_left_team(self, data: Any):
        self.dispatch("user_left_team")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_user_joined_voice_channel(self, data: Any):
        self.dispatch("user_joinded_voice_channel")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_user_left_voice_channel(self, data: Any):
        self.dispatch("user_left_voice_channel")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_user_profile_updated(self, data: Any):
        self.dispatch("user_profile_updated")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_user_role_added(self, data: Any):
        self.dispatch("user_role_added")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_user_role_removed(self, data: Any):
        self.dispatch("user_role_removed")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_user_updated_voice_metadata(self, data: Any):
        self.dispatch("user_updated_voice_metadata")
        print(json.dumps(data,indent=4, ensure_ascii=False))




    def parse_blog_created(self, data: Any):
        self.dispatch("blog")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_blog_deleted(self, data: Any):
        self.dispatch("blog_deleted")
        print(json.dumps(data,indent=4, ensure_ascii=False))




    def parse_categories_priority_updated(self, data: Any):
        self.dispatch("categories_priority_updated")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_category_updated(self, data: Any):
        self.dispatch("category_updated")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_category_deleted(self, data: Any):
        self.dispatch("category_deleted")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_category_created(self, data: Any):
        self.dispatch("category")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_channels_priority_updated(self, data: Any):
        self.dispatch("channels_priority_updated")
        print(json.dumps(data,indent=4, ensure_ascii=False))




    def parse_announcement_created(self, data: Any):
        self.dispatch("announcement")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_announcement_deleted(self, data: Any):
        self.dispatch("announcement_deleted")
        print(json.dumps(data,indent=4, ensure_ascii=False))




    def parse_application_created(self, data: Any):
        self.dispatch("application")
        print(json.dumps(data,indent=4, ensure_ascii=False))

    def parse_application_updated(self, data: Any):
        self.dispatch("application_updated")
        print(json.dumps(data,indent=4, ensure_ascii=False))




    def parse_voice_channel_move(self, data: Any):
        self.dispatch("voice_channel_move")
        print(json.dumps(data,indent=4, ensure_ascii=False))
