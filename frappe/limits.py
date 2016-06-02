from __future__ import unicode_literals
import frappe
import subprocess, os
from frappe.model.document import Document
from frappe.core.doctype.user.user import get_total_users
from frappe.utils import flt, cint, now_datetime, getdate, get_site_path
from frappe.utils.file_manager import MaxFileSizeReachedError
from frappe import _



def update_sizes():
	from frappe.installer import update_site_config
	# public files
	files_path = frappe.get_site_path("public", "files")
	files_size = flt(subprocess.check_output("du -ms {0}".format(files_path), shell=True).split()[0])

	# private files
	files_path = frappe.get_site_path("private", "files")
	if os.path.exists(files_path):
		files_size += flt(subprocess.check_output("du -ms {0}".format(files_path), shell=True).split()[0])

	# backups
	backup_path = frappe.get_site_path("private", "backups")
	backup_size = subprocess.check_output("du -ms {0}".format(backup_path), shell=True).split()[0]

	database_path = os.path.join('/home/frappe', "database_sizes.txt")

	database_size = 26
	if os.path.exists(database_path):
		with open(database_path, "r") as database_sizes:
			for t in database_sizes.read().splitlines():
				parts = t.split()
				if parts[1] == frappe.conf.db_name:
					database_size = parts[0]
					break

	d = frappe.get_conf().get("limits")
	d['files_size'] = files_size
	d['backup_size'] = backup_size
	d['database_size'] = database_size
	update_site_config("limits", d, validate=False)


def has_expired():
	if not frappe.conf.get("stop_on_expiry") or frappe.session.user=="Administrator":
		return False

	expires_on = get_frappe_limits().get("expires_on")
	if not expires_on:
		return False

	if now_datetime().date() <= getdate(expires_on):
		return False

	return True


def check_if_expired():
	"""check if account is expired. If expired, do not allow login"""
	if not has_expired():
		return

	# if expired, stop user from logging in
	expires_on = formatdate(get_frappe_limits().get("expires_on"))

	frappe.throw("""Your subscription expired on <b>{}</b>.
		To extend please drop a mail at <b>support@erpnext.com</b>""".format(expires_on),
		frappe.AuthenticationError)

@frappe.whitelist()
def get_limits():
	print frappe.get_conf().get("limits")
	return frappe.get_conf().get("limits")


def set_limits(limits):
	from frappe.installer import update_site_config

	if not limits:
		frappe_limits = 'None'
	else:
		frappe_limits = frappe.get_conf().get("limits") or {}
		for key in limits.keys():
			frappe_limits[key] = limits[key]

	update_site_config("limits", frappe_limits, validate=False)
