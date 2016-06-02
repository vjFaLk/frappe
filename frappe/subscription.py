from __future__ import unicode_literals
import frappe
import subprocess, os
from frappe.model.document import Document
from frappe.core.doctype.user.user import get_total_users
from frappe.utils import flt, cint, now_datetime, getdate, get_site_path
from frappe.utils.file_manager import MaxFileSizeReachedError
from frappe import _


def validate_max_users(doc, method):
	"""
		This is called using validate hook, because welcome email is sent in on_update.
		We don't want welcome email sent if max users are exceeded.
	"""
	subscription_info = get_subscription_info()

	if frappe.flags.in_test or doc.user_type == "Website User":
		return

	if not doc.enabled:
		# don't validate max users when saving a disabled user
		return

	max_users = subscription_info.get("user_limit")

	if not max_users:
		return

	total_users = get_total_users()

	if doc.is_new():
		# get_total_users gets existing users in database
		# a new record isn't inserted yet, so adding 1
		total_users += 1

	if total_users > max_users:
		print 'In here to compare'
		frappe.throw(_("Sorry. You have reached the maximum user limit for your subscription. You can either disable an existing user or buy a higher subscription plan."))

def validate_max_space(file_size):
	"""Stop from writing file if max space limit is reached"""
	frappe_subscription = get_subscription_info()

	if not frappe_subscription.max_space:
		return

	# In Gigabytes
	max_space = flt(flt(frappe_subscription.max_space) * 1024, 2)

	# in Kilobytes
	used_space = flt(frappe_subscription.files_size) + flt(frappe_subscription.backup_size) + flt(frappe_subscription.database_size)
	file_size = file_size / (1024.0**2)

	# Stop from attaching file
	if flt(used_space + file_size, 2) > max_space:
		frappe.throw(_("You have exceeded the max space of {0} for your plan. {1} or {2}.").format(
			"<b>{0}MB</b>".format(cint(max_space)) if (max_space < 1024) else "<b>{0}GB</b>".format(frappe_subscription.max_space),
			'<a href="#usage-info">{0}</a>'.format(_("Click here to check your usage")),
			'<a href="#upgrade">{0}</a>'.format(_("upgrade to a higher plan")),
		), MaxFileSizeReachedError)

	# update files size in frappe subscription
	new_files_size = flt(frappe_subscription.files_size) + file_size
	frappe.db.set_value("Frappe Subscription Info", "Frappe Subscription Info", "files_size", new_files_size)


def update_sizes():
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

	d = frappe.get_doc("Frappe Subscription Info")
	d.files_size = files_size
	d.backup_size = backup_size
	d.database_size = database_size
	d.flags.ignore_permissions = True
	d.flags.ignore_mandatory = True
	d.save()

def disable_scheduler_on_expiry():
	if has_expired():
		disable_scheduler()

def has_expired():
	if not frappe.conf.get("stop_on_expiry") or frappe.session.user=="Administrator":
		return False

	expires_on = get_subscription_info().get("expires_on")
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
	expires_on = formatdate(get_subscription_info().get("expires_on"))

	frappe.throw("""Your subscription expired on <b>{}</b>.
		To extend please drop a mail at <b>support@erpnext.com</b>""".format(expires_on),
		frappe.AuthenticationError)

def reset_enabled_scheduler_events(login_manager):
	if login_manager.info.user_type == "System User":
		try:
			frappe.db.set_global('enabled_scheduler_events', None)
		except MySQLdb.OperationalError, e:
			if e.args[0]==1205:
				frappe.get_logger().error("Error in reset_enabled_scheduler_events")
			else:
				raise
		else:
			dormant_file = get_site_path('dormant')
			if os.path.exists(dormant_file):
				os.remove(dormant_file)


def restrict_scheduler_events_if_dormant():
	if is_dormant():
		restrict_scheduler_events()
		touch_file(get_site_path('dormant'))

		
def disable_scheduler_on_expiry():
	if has_expired():
		from frappe.utils.scheduler import disable_scheduler
		disable_scheduler()


def get_subscription_info():
	return frappe.get_doc("Frappe Subscription Info", "Frappe Subscription Info").as_dict()