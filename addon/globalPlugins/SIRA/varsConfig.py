# -*- coding: UTF-8 -*-

"""
Author: Edilberto Fonseca <edilberto.fonseca@outlook.com>
Copyright: (C) 2025 Edilberto Fonseca

This file is covered by the GNU General Public License.
See the file COPYING for more details or visit:
https://www.gnu.org/licenses/gpl-2.0.html

Created on: 08/01/2025.
"""

import os

import addonHandler
import config
from logHandler import log

# Constantes
mask_date = "XX/XX/XXXX"
mask_time = "XX:XX"
mask_phone = "(XX) XXXXX-XXXX"

# Get the path to the root of the current add-on
addonPath = os.path.dirname(__file__)

# Config# Get the add-on summary contained in the manifest.
ADDON_NAME = addonHandler.getCodeAddon().manifest["name"]
ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]
ADDON_DESCRIPTION = addonHandler.getCodeAddon().manifest["description"]
ADDON_VERSION = addonHandler.getCodeAddon().manifest["version"]


def getOurAddon():
	"""
	Retrieves the current add-on.
	Returns:
		addonHandler.Addon: The current add-on instance.
	"""
	try:
		return addonHandler.getCodeAddon()
	except Exception as e:
		log.error(f"Error getting the add-on: {e}")


# Retrieve the current add-on instance
ourAddon = getOurAddon()


def initConfiguration():
	"""
	Initializes the configuration specification for the Contacts Manager for NVDA add-on.
	"""
	try:
		confspec = {
			"formatLandline": """string(default="(##) ####-####")""",
			"formatCellPhone": """string(default="(##) #####-####")""",
			"resetRecords": "boolean(default=True)",
			"importCSV": "boolean(default=True)",
			"exportCSV": "boolean(default=True)",
			"path": "string(default="")",
			"altPath": "string(default="")",
			#"xx": "string(default="")",
			"databaseIndex": "integer(default=0)",
		}
		config.conf.spec[ourAddon.name] = confspec
	except Exception as e:
		log.error("Error initializing configuration: {}".format(str(e)))


# Initialize the configuration
initConfiguration()
