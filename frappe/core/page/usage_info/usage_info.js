frappe.pages['usage-info'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Subscription Info',
		single_column: true
	});

	frappe.model.with_doc("Frappe Subscription Info", "Frappe Subscription Info", function() {
		var doc = frappe.get_doc("Frappe Subscription Info", "Frappe Subscription Info");
		if(!doc.database_size) doc.database_size = 26;
		if(!doc.files_size) doc.files_size = 1;
		if(!doc.backup_size) doc.backup_size = 1;

		doc.max = flt(doc.max_space * 1024);
		doc.total = (doc.database_size + doc.files_size + doc.backup_size);
		doc.users = keys(frappe.boot.user_info).length - 2;
		doc.plan = "Plan"

		$(frappe.render_template("usage_info", doc)).appendTo(page.main);

		//var btn_text = ["Free", "Free-Solo"].indexOf(doc.plan)!==-1 ? __("Upgrade") : __("Renew / Upgrade");

		// if(doc.__onload.allow_upgrade) {
		// 	page.set_primary_action(btn_text, function() {
		// 		frappe.set_route("upgrade");
		// 	});
		// }

	});
}
	