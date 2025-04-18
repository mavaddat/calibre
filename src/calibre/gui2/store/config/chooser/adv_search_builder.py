__license__ = 'GPL 3'
__copyright__ = '2011, John Schember <john@nachtimwald.com>'
__docformat__ = 'restructuredtext en'

import re

from qt.core import QDialog, QDialogButtonBox

from calibre.gui2.store.config.chooser.adv_search_builder_ui import Ui_Dialog
from calibre.library.caches import CONTAINS_MATCH, EQUALS_MATCH
from calibre.utils.localization import localize_user_manual_link


class AdvSearchBuilderDialog(QDialog, Ui_Dialog):

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        try:
            self.sh_label.setText(self.sh_label.text() % localize_user_manual_link(
                'https://manual.calibre-ebook.com/gui.html#the-search-interface'))
        except TypeError:
            pass  # link already localized

        self.buttonBox.accepted.connect(self.advanced_search_button_pushed)
        self.tab_2_button_box.accepted.connect(self.accept)
        self.tab_2_button_box.rejected.connect(self.reject)
        self.clear_button.clicked.connect(self.clear_button_pushed)
        self.adv_search_used = False
        self.mc = ''

        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.currentChanged[int].connect(self.tab_changed)
        self.tab_changed(0)

    def tab_changed(self, idx):
        if idx == 1:
            self.tab_2_button_box.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)
        else:
            self.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setDefault(True)

    def advanced_search_button_pushed(self):
        self.adv_search_used = True
        self.accept()

    def clear_button_pushed(self):
        self.name_box.setText('')
        self.description_box.setText('')
        self.headquarters_box.setText('')
        self.format_box.setText('')
        self.enabled_combo.setCurrentIndex(0)
        self.drm_combo.setCurrentIndex(0)
        self.affiliate_combo.setCurrentIndex(0)

    def tokens(self, raw):
        phrases = re.findall(r'\s*".*?"\s*', raw)
        for f in phrases:
            raw = raw.replace(f, ' ')
        phrases = [t.strip('" ') for t in phrases]
        return ['"' + self.mc + t + '"' for t in phrases + [r.strip() for r in raw.split()]]

    def search_string(self):
        if self.adv_search_used:
            return self.adv_search_string()
        else:
            return self.box_search_string()

    def adv_search_string(self):
        mk = self.matchkind.currentIndex()
        if mk == CONTAINS_MATCH:
            self.mc = ''
        elif mk == EQUALS_MATCH:
            self.mc = '='
        else:
            self.mc = '~'
        all, any, phrase, none = (str(x.text()) for x in (self.all, self.any, self.phrase, self.none))
        all, any, none = map(self.tokens, (all, any, none))
        phrase = phrase.strip()
        all = ' and '.join(all)
        any = ' or '.join(any)
        none = ' and not '.join(none)
        ans = ''
        if phrase:
            ans += f'"{phrase}"'
        if all:
            ans += (' and ' if ans else '') + all
        if none:
            ans += (' and not ' if ans else 'not ') + none
        if any:
            ans += (' or ' if ans else '') + any
        return ans

    def token(self):
        txt = str(self.text.text()).strip()
        if txt:
            if self.negate.isChecked():
                txt = '!'+txt
            tok = self.FIELDS[str(self.field.currentText())]+txt
            if re.search(r'\s', tok):
                tok = f'"{tok}"'
            return tok

    def box_search_string(self):
        mk = self.matchkind.currentIndex()
        if mk == CONTAINS_MATCH:
            self.mc = ''
        elif mk == EQUALS_MATCH:
            self.mc = '='
        else:
            self.mc = '~'

        ans = []
        self.box_last_values = {}
        name = str(self.name_box.text()).strip()
        if name:
            ans.append('name:"' + self.mc + name + '"')
        description = str(self.description_box.text()).strip()
        if description:
            ans.append('description:"' + self.mc + description + '"')
        headquarters = str(self.headquarters_box.text()).strip()
        if headquarters:
            ans.append('headquarters:"' + self.mc + headquarters + '"')
        format = str(self.format_box.text()).strip()
        if format:
            ans.append('format:"' + self.mc + format + '"')
        enabled = str(self.enabled_combo.currentText()).strip()
        if enabled:
            ans.append('enabled:' + enabled)
        drm = str(self.drm_combo.currentText()).strip()
        if drm:
            ans.append('drm:' + drm)
        affiliate = str(self.affiliate_combo.currentText()).strip()
        if affiliate:
            ans.append('affiliate:' + affiliate)
        if ans:
            return ' and '.join(ans)
        return ''
