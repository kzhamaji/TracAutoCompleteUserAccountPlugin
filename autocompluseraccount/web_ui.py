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
        if template in ('ticket.html', 'query.html'):
            Chrome(self.env).add_jquery_ui(req)
            add_script(req, self.ID + '/js/autocompluseraccount.js')
            if template == 'query.html':
                add_script(req, self.ID + '/js/jquery-observe.js')
        return template, data, content_type


    # ITemplateStreamFilter
    def filter_stream (self, req, method, filename, stream, data):
        if filename not in ('ticket.html', 'query.html'):
            return stream

        if filename == 'ticket.html':
            for xpath in [self._item_to_xpath_t(f) for f in self.single_fields]:
                stream |= Transformer(xpath).attr('class', self.CLASS)

            for xpath in [self._item_to_xpath_t(f) for f in self.multiple_fields]:
                stream |= Transformer(xpath).attr('class', self.CLASS_MULTI)

        if filename == 'query.html':
            for xpath in [self._item_to_xpath_q(f) for f in self.single_fields]:
                stream |= Transformer(xpath).attr('class', self.CLASS)

            for xpath in [self._item_to_xpath_q(f) for f in self.multiple_fields]:
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

    def _item_to_xpath_t (self, item):
        if item.startswith('.'):
            return '//input[@class="' + item[1:] + '"]'
        if item.startswith('#'):
            return '//input[@id="' + item[1:] + '"]'
        return '//input[@id="field-' + item + '"]'

    def _item_to_xpath_q (self, item):
        if item.startswith('.'):
            return '//input[@class="' + item[1:] + '"]'
        if item.startswith('#'):
            return '//input[@id="' + item[1:] + '"]'
        return '//fieldset[@id="filters"]//tr[@class="' + item + '"]'\
                '/td[@class="filter"]/input'

    def _is_field (self, item):
        return item[0] not in ('.', '#')


    # IRequestHandler methods
    def match_request(self, req):
        return req.path_info.startswith('/accounts_completion')

    def process_request(self, req):
        users = []
        for username, name, email in self.env.get_known_users():
            info = { 'value': username }
            if self.enable_name:
                info['name'] = name
            if self.enable_avatar and has_UserPictureModule:
                upm = UserPicturesModule(self.env)
                avatar = upm._generate_avatar(req,
                            username, self.CLASS, 20).render()
                info['avatar'] = avatar

            users.append(info)
        users.sort(key=lambda i: i['value'])

        data = {
            'users': users,
            'single': [f for f in self.single_fields if self._is_field(f)],
            'multi': [f for f in self.multiple_fields if self._is_field(f)],
        }
        req.send(json.dumps(data).encode('utf-8'), 'application/json')
