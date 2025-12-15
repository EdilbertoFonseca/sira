# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 30/11/2022.
"""

import os

import addonHandler
import config
import gui
import queueHandler
import ui
import wx
from gui import guiHelper

from . import controller as core
from .addEditRecord import AddEditRecDialog
from .varsConfig import ADDON_SUMMARY, ourAddon
from .manageDuplicatesDialog import ManageDuplicatesDialog

# Initializes the translation
addonHandler.initTranslation()


class SIRA(wx.Dialog):
	_instance = None

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(SIRA, cls).__new__(cls, *args, **kwargs)
		else:
			msg = _("An instance of {} is already open!").format(ADDON_SUMMARY)
			queueHandler.queueFunction(queueHandler.eventQueue, ui.message, msg)
		return cls._instance

	def __init__(self, parent, title):
		if hasattr(self, "initialized"):
			return
		self.initialized = True

		self.title = title

		WIDTH = 800
		HEIGHT = 400

		try:
			self.contactResults = core.get_all_records()
		except EOFError:
			self.contactResults = []

		super(SIRA, self).__init__(
			parent, title=title, size=(WIDTH, HEIGHT), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
		)

		self.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)

		# --------- UI ---------
		panel = wx.Panel(self)
		self.contactList = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		self.initialize_contact_list()
		self.contactList.SetFocus()

		self.visualizationField = wx.TextCtrl(
			panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_STATIC
		)

		labelSearch = wx.StaticText(panel, label=_("Search for: "))
		listOfOptions = [
			_("Secretary office"), _("Landline"), _("Sector"), _("Responsible"),
			_("Extension"), _("Cell phone"), _("Email")
		]
		self.comboboxOptions = wx.ComboBox(panel, value=_("Secretary office"), choices=listOfOptions)

		self.search = wx.SearchCtrl(panel, -1, size=(250, 25))
		self.buttonSearch = wx.Button(panel, label=_("&Search"))

		self.contactList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelectLine)

		self.buttonEdit = wx.Button(panel, wx.ID_EDIT, label=_("&Edit"))
		self.buttonNew = wx.Button(panel, wx.ID_NEW, label=_("&New"))
		self.buttonDelete = wx.Button(panel, wx.ID_DELETE, label=_("&Remove"))
		self.buttonFindDuplicates = wx.Button(panel, label=_("Find Duplicates"))
		self.buttonSaveResearch = wx.Button(panel, wx.ID_SAVE, label=_("&Save the research"))
		self.buttonRefresh = wx.Button(panel, -1, label=_("Refres&h"))
		self.buttonImport = wx.Button(panel, -1, label=_("&Import csv..."))
		self.buttonExport = wx.Button(panel, -1, label=_("E&xport csv..."))
		self.buttonResetRecords = wx.Button(panel, -1, label=_("&Delete all records."))
		self.buttonExit = wx.Button(panel, wx.ID_CANCEL, label=_("Exi&t"))

		self.set_config()

		# --------- LAYOUT ---------
		boxSizer = wx.BoxSizer(wx.VERTICAL)
		viewSizer = wx.BoxSizer(wx.VERTICAL)
		searchSizer = wx.BoxSizer(wx.HORIZONTAL)
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)

		viewSizer.Add(self.contactList, 1, wx.ALL | wx.EXPAND, 10)
		searchSizer.Add(labelSearch, 0, wx.ALL, 5)
		searchSizer.Add(self.comboboxOptions, 0, wx.ALL, 5)
		searchSizer.Add(self.search, 1, wx.ALL, 5)
		searchSizer.Add(self.buttonSearch, 0, wx.ALL, 5)

		buttonSizer.Add(self.buttonEdit, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonDelete, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonFindDuplicates, 0, wx.ALL, 5)
		buttonSizer.Add(self.buttonSaveResearch, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonRefresh, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonImport, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonExport, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonResetRecords, 0, wx.ALL | wx.EXPAND, 5)
		buttonSizer.Add(self.buttonExit, 0, wx.ALL | wx.EXPAND, 5)

		boxSizer.Add(searchSizer, wx.ALL, guiHelper.BORDER_FOR_DIALOGS)
		boxSizer.Add(viewSizer, wx.ALL, guiHelper.BORDER_FOR_DIALOGS)
		boxSizer.Add(buttonSizer, 0, wx.CENTER)
		panel.SetSizerAndFit(boxSizer)
		self.Fit()

		# --------- EVENTS ---------
		self.buttonSearch.Bind(wx.EVT_BUTTON, self.onSearch)
		self.buttonEdit.Bind(wx.EVT_BUTTON, self.onEdit)
		self.buttonNew.Bind(wx.EVT_BUTTON, self.onNew)
		self.buttonDelete.Bind(wx.EVT_BUTTON, self.onDelete)
		self.buttonFindDuplicates.Bind(wx.EVT_BUTTON, self.onFindDuplicates)
		self.buttonSaveResearch.Bind(wx.EVT_BUTTON, self.onSaveResearchResults)
		self.buttonRefresh.Bind(wx.EVT_BUTTON, self.onToUpdate)
		self.buttonImport.Bind(wx.EVT_BUTTON, self.onToImport)
		self.buttonExport.Bind(wx.EVT_BUTTON, self.onToExport)
		self.buttonResetRecords.Bind(wx.EVT_BUTTON, self.onReset)
		self.buttonExit.Bind(wx.EVT_BUTTON, self.onClose)


	# =====================================================================
	#        LISTA + MAPEAMENTO SEGURO PARA NVDA — CORREÇÃO FINAL
	# =====================================================================
	def initialize_contact_list(self):
		self.contactList.ClearAll()
		self._itemMap = {}

		columns = [
			(_("Secretary office"), 150),
			(_("Landline"), 100),
			(_("Sector"), 150),
			(_("Responsible"), 150),
			(_("Extension"), 100),
			(_("Cell phone"), 100),
			(_("Email"), 300),
		]
		for i, (title, width) in enumerate(columns):
			self.contactList.InsertColumn(i, title, width=width)

		for rowIndex, record in enumerate(self.contactResults):

			i = self.contactList.InsertItem(self.contactList.GetItemCount(), record.secretary_office)

			values = (
				record.landline,
				record.sector,
				record.responsible,
				record.extension,
				record.cell,
				record.email
			)

			for col, value in enumerate(values, start=1):
				self.contactList.SetItem(i, col, value)

			# Guarda objeto REAL
			self._itemMap[i] = record

			# Guarda apenas o índice no ListCtrl → seguro e compatível
			self.contactList.SetItemData(i, i)


	# =====================================================================

	def get_selected_record(self):
		index = self.contactList.GetFirstSelected()
		if index == -1:
			return None
		return self._itemMap.get(index)


	# =====================================================================

	def onNew(self, event):
		dlg = AddEditRecDialog(gui.mainFrame)
		gui.mainFrame.prePopup()
		dlg.ShowModal()
		gui.mainFrame.postPopup()
		self._refresh_and_focus()

	def onEdit(self, event):
		selected = self.get_selected_record()
		if not selected:
			self.show_message(_("No records selected!"), _("Error"))
			return

		dlg = AddEditRecDialog(
			gui.mainFrame,
			selected,
			title=_("To edit"),
			addRecord=False
		)
		gui.mainFrame.prePopup()
		dlg.ShowModal()
		gui.mainFrame.postPopup()
		self._refresh_and_focus()

	def onDelete(self, event):
		selected = self.get_selected_record()
		if not selected:
			self.show_message(_("No records selected!"), _("Error"))
			return

		if gui.messageBox(_("Do you want to delete the selected record?"),
						  _("Attention"), wx.YES_NO) == wx.YES:
			try:
				core.delete(selected.id)
			except Exception as e:
				self.show_message(_("Error deleting record: {}").format(str(e)))
				return

			self.show_message(_("Record deleted!"))
			self._refresh_and_focus()

	def onSearch(self, event):
		filterChoice = self.comboboxOptions.GetValue()
		keyword = self.search.GetValue()

		if not keyword.strip():
			self.show_message(_("The search field is empty!"))
			self.search.SetFocus()
			return

		try:
			self.contactResults = core.search_records(filterChoice, keyword)
			if not self.contactResults:
				self.show_message(_("No contacts found matching the search criteria."))
				self.search.SetFocus()
			else:
				self.initialize_contact_list()
				self.search.Clear()
				self.contactList.SetFocus()
		except Exception as e:
			self.show_message(str(e))

	def onToImport(self, event):
		dlg = wx.FileDialog(self, _("import csv file"), os.getcwd(), "", "*.csv", wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				core.import_csv_to_db(dlg.GetPath())
				self.show_message(_("File imported successfully!"))
				self._refresh_and_focus()
			except Exception as e:
				self.show_message(_("It was not possible to import the file! {}").format(str(e)))
		dlg.Destroy()
		self.contactList.SetFocus()

	def onToExport(self, event):
		dlg = wx.FileDialog(
			self,
			_("export csv file"),
			os.getcwd(),
			_("List of extensions"),
			"*.csv",
			wx.FD_SAVE
		)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				core.export_db_to_csv(dlg.GetPath())
				self.show_message(_("File exported successfully!"))
			except Exception as e:
				self.show_message(_("It was not possible to export the file! {}").format(e))
		dlg.Destroy()
		self.contactList.SetFocus()

	def onReset(self, event):
		count = core.count_records()
		if count is None:
			self.show_message(_("Error counting records."), _("Error"))
			return
		if count == 0:
			self.show_message(_("The agenda is already empty!"))
			return

		if gui.messageBox(_("This operation erases all phonebook entries. Do you wish to continue?"),
						  _("Attention"), wx.YES_NO) == wx.YES:
			try:
				core.reset_record()
				self.show_message(_("Agenda deleted!"))
			except Exception as e:
				self.show_message(_("Error deleting records: {}").format(str(e)))
		self._refresh_and_focus()

	def set_config(self):
		if not config.conf[ourAddon.name]["resetRecords"]:
			self.buttonResetRecords.Disable()
		if (not config.conf[ourAddon.name]["importCSV"]) or (not config.conf[ourAddon.name]["exportCSV"]):
			self.buttonExport.Disable()
			self.buttonImport.Disable()

	def onFindDuplicates(self, event):
		duplicates = core.find_duplicate_records()

		if duplicates:
			dlg = ManageDuplicatesDialog(self, duplicates)
			gui.mainFrame.prePopup()
			dlg.ShowModal()
			gui.mainFrame.postPopup()
		else:
			gui.messageBox(_("No duplicate records were found."),
						   _("No Duplicates Found"),
						   style=wx.ICON_INFORMATION)

	def onSaveResearchResults(self, event):
		filtered_item = self.contactResults

		if not filtered_item:
			self.show_message("No results found to save.", "Warning")
			return

		dlg = wx.FileDialog(
			self,
			_("export csv file"),
			os.getcwd(),
			_("List of extensions"),
			"*.csv",
			wx.FD_SAVE
		)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				core.save_csv(filtered_item, dlg.GetPath())
				self.show_message(_("File exported successfully!"))
			except Exception as e:
				self.show_message(_("It was not possible to export the file! {}").format(e))
		dlg.Destroy()
		self.contactList.SetFocus()

	def show_message(self, message, caption=_("Message"), style=wx.OK | wx.ICON_INFORMATION):
		gui.messageBox(message, caption, style)

	def onKeyPress(self, event):
		keyCode = event.GetKeyCode()
		if keyCode == wx.WXK_F5:
			self.onToUpdate(event)
		elif keyCode == wx.WXK_DELETE:
			focused = self.FindFocus()
			if isinstance(focused, (wx.TextCtrl, wx.SearchCtrl)):
				event.Skip()
				return
			self.onDelete(event)
		elif keyCode == wx.WXK_F2:
			self.onEdit(event)
		event.Skip()

	def onClose(self, event):
		self.Destroy()

	def show_all_records(self):
		self.contactResults = core.get_all_records()
		self.initialize_contact_list()

	def _refresh_and_focus(self):
		self.show_all_records()
		self.visualizationField.SetValue("")
		self.contactList.SetFocus()

	def onToUpdate(self, event):
		self._refresh_and_focus()
		ui.message(_("Updated records!"))

	def onSelectLine(self, event):
		selected_idx = self.contactList.GetFirstSelected()
		if selected_idx == -1:
			return

		data = [
			f"{self.contactList.GetColumn(i).GetText()}: {self.contactList.GetItem(selected_idx, i).GetText()}"
			for i in range(self.contactList.GetColumnCount())
		]
		lineComplete = " | ".join(data)
		self.visualizationField.SetValue(lineComplete)
