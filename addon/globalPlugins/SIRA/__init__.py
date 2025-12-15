# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 25/02/2025
"""

import os

import addonHandler
import globalPluginHandler
import globalVars
import gui
import wx
from logHandler import log
from scriptHandler import script

from .configPanel import SIRASystemSettingsPanel
from .generalMessage import GeneralMessage
from .main import SIRA
from .medicalDischarge import MedicalDischarge
from .messageForTransport import MessageForTransport
from .model import Section
from .varsConfig import ADDON_NAME, ADDON_SUMMARY

# Start the initDB function.
Section.initDB()

# Initialize translation support
addonHandler.initTranslation()

def disableInSecureMode(decoratedCls):
	"""
	Decorator to disable the plugin in secure mode.
	"""
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls


@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	# Creating the constructor of the newly created GlobalPlugin class.
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.create_menu()

	def create_menu(self):
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(SIRASystemSettingsPanel)
		self.mainMenu = wx.Menu()
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu

		# Creation of menu items.
		self.registeredExtensions = self.mainMenu.Append(-1, _("&Lists Of Registered Extensions..."))
		self.messageForTransport= self.mainMenu.Append(-1, _("&Message for transport..."))
		self.medicalDischarge = self.mainMenu.Append(-1, _("Medical discharge &register..."))
		self.generalMessage= self.mainMenu.Append(-1, _("&General message..."))
		self.settingsPanel = self.mainMenu.Append(-1, _("&Settings..."))
		self.help = self.mainMenu.Append(-1, _('&Help'))

    # Binding Events
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_activateListOfRegisteredExtensions, self.registeredExtensions)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_activateMessageForTransport, self.messageForTransport)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_activateMedicalDischarge, self.medicalDischarge)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_activateGeneralMessage, self.generalMessage)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_openAddonSettingsDialog, self.settingsPanel)
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.script_onHelp, self.help)

		self.toolsMenu.AppendSubMenu(self.mainMenu, "&{}...".format(ADDON_SUMMARY))

	def onSIRA(self, event):
		# Translators: Title of contact list dialog box.
		self.dlg = SIRA(gui.mainFrame, _("Lists Of Registered Extensions."))
		gui.mainFrame.prePopup()
		self.dlg.CentreOnScreen()
		self.dlg.Show()
		gui.mainFrame.postPopup()

	def onMessageForTransport(self, event):
		# Translators: Addon's main window dialog
		self.dlg = MessageForTransport(gui.mainFrame, _(
			"Message for transport."))
		gui.mainFrame.prePopup()
		self.dlg.CentreOnScreen()
		self.dlg.Show()
		gui.mainFrame.postPopup()

	def onMedicalDischarge(self, event):
		# Translators: Addon's main window dialog
		self.dlg = MedicalDischarge(gui.mainFrame,
		_("Medical discharge register"))
		gui.mainFrame.prePopup()
		self.dlg.CentreOnScreen()
		self.dlg.Show()
		gui.mainFrame.postPopup()

	def onGeneralMessage(self, event):
		# Translators: Addon's main window dialog
		self.dlg = GeneralMessage(gui.mainFrame,
		_("General Message"))
		gui.mainFrame.prePopup()
		self.dlg.CentreOnScreen()
		self.dlg.Show()
		gui.mainFrame.postPopup()

	# defining a script with decorator:
	@script(
		gesture="kb:Alt+numpad1",
		# Translators: Text displayed in NVDA help.
		description=_("%s - Displays a window with all contacts registered in the Extension Registration System.") % ADDON_NAME,
		category=ADDON_SUMMARY
	)
	def script_activateListOfRegisteredExtensions(self, gesture):
		wx.CallAfter(self.onSIRA, None)

	# defining a script with decorator:
	@script(
		gesture="kb:Alt+numpad2",
		# Translators: Text displayed in NVDA help.
		description=_("%s - Message logging for the Transportation Department.") % ADDON_NAME,
		category=ADDON_SUMMARY
	)
	def script_activateMessageForTransport(self, gesture):
			wx.CallAfter(self.onMessageForTransport, None)

	# defining a script with decorator:
	@script(
		gesture="kb:Alt+numpad3",
		# Translators: Text displayed in NVDA help.
		description=_("%s - Hospital Discharge Registration.") % ADDON_NAME,
		category=ADDON_SUMMARY
	)
	def script_activateMedicalDischarge(self, gesture):
			wx.CallAfter(self.onMedicalDischarge, None)

	# defining a script with decorator:
	@script(
		gesture="kb:Alt+numpad4",
		# Translators: Text displayed in NVDA help.
		description=_("%s - Allows the registration of messages for all departments.") % ADDON_NAME,
		category=ADDON_SUMMARY
	)
	def script_activateGeneralMessage(self, gesture):
			wx.CallAfter(self.onGeneralMessage, None)

	def script_openAddonSettingsDialog(self, gesture):
		wx.CallAfter(
			getattr(gui.mainFrame, "popupSettingsDialog", gui.mainFrame._popupSettingsDialog),
			gui.settingsDialogs.NVDASettingsDialog,
			SIRASystemSettingsPanel
		)

	def script_onHelp(self, gesture):
		"""Open the addon's help page"""
		wx.LaunchDefaultBrowser(addonHandler.Addon(os.path.join(
			os.path.dirname(__file__), "..", "..")).getDocFilePath())

	def terminate(self):
		super(GlobalPlugin, self).terminate()
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(
			SIRASystemSettingsPanel)
		try:
			self.toolsMenu.Remove(self.mainMenu)
		except Exception as e:
			log.warning(f"Error removing Scraps and agenda organizer menu item: {e}")
