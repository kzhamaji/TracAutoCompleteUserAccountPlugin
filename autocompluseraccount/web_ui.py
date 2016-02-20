# encoding: utf-8

import json

from pkg_resources import resource_filename

from genshi.filters.transform import Transformer
from genshi.builder import tag

from trac.core import Component, implements
from trac.config import BoolOption, ListOption
from trac.web.chrome import Chrome
from trac.util.compat import *
from trac.web.api import IRequestFilter, ITemplateStreamFilter, IRequestHandler
from trac.web.chrome import ITemplateProvider, add_script, add_stylesheet

try:
    from userpictures import UserPicturesModule
    has_UserPictureModule = True
except ImportError:
    has_UserPictureModule = False


class TicketAutoCompleteUserPlugin (Component):

    ID = 'autocompluseraccount'
    SECTION = ID
    CLASS = ID
    CLASS_MULTI = ID + '-multi'

    enable_avatar = BoolOption(SECTION, 'avatar', False)
    enable_name = BoolOption(SECTION, 'name', False)

    single_fields = ListOption(SECTION, 'single', ['reporter', 'owner'])
    multiple_fields = ListOption(SECTION, 'multiple', ['cc'])

    implements(ITemplateProvider, IRequestFilter, ITemplateStreamFilter, IRequestHandler)

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        yield self.ID, resource_filename(__name__, 'htdocs')
    def get_templates_dirs(self):
        return []


    # IRequestFilter
    def pre_process_request (self, req, handler):
        return handler
    def post_process_request (self, req, template, data, content_type):
        if req.path_info.startswith('/newticket') or\
           req.path_info.startswith('/ticket/'):
            Chrome(self.env).add_jquery_ui(req)
            add_script(req, 'autocompluseraccount/js/autocompluseraccount.js')
        return template, data, content_type


    # ITemplateStreamFilter
    def filter_stream (self, req, method, filename, stream, data):
        if not req.path_info.startswith('/newticket') and\
           not req.path_info.startswith('/ticket/'):
            return stream

        for xpath in [self._item_to_xpath(f) for f in self.single_fields]:
            stream |= Transformer(xpath).attr('class', self.CLASS)

        for xpath in [self._item_to_xpath(f) for f in self.multiple_fields]:
            stream |= Transformer(xpath).attr('class', self.CLASS_MULTI)


        stream |= Transformer('//head').append(tag.style('''
            img.autocompluseraccount { vertical-align: middle; }
            ul.ui-autocomplete li.ui-menu-item span.username {
              font-size: 0.85em;
              font-style: italic;
              color: #888;
            }
            '''))
        return stream

    def _item_to_xpath (self, item):
        if item.startswith('.'):
            return '//input[@class="' + item[1:] + '"]' 
        if item.startswith('#'):
            return '//input[@id="' + item[1:] + '"]' 

        return '//*[@id="field-' + item + '"]'


    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info.startswith('/accounts_completion')

    def process_request(self, req):
        data = []
        for username, name, email in self.env.get_known_users():
            info = { 'value': username }
            if self.enable_name:
                info['name'] = name
            if self.enable_avatar and has_UserPictureModule:
                upm = UserPicturesModule(self.env)
                avatar = upm._generate_avatar(req,
                            username, self.CLASS, 20).render()
                info['avatar'] = avatar

            data.append(info)
        data.sort(key=lambda i: i['value'])
        req.send(json.dumps(data).encode('utf-8'), 'application/json')
