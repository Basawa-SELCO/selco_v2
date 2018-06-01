frappe.query_reports["Pending Rejection Out To Customer"] = {
	"filters": [
		{
				"fieldname":"selco_branch",
				"label": __("Branch"),
				"fieldtype": "Link",
				"options": "Branch"
		}

	]
}