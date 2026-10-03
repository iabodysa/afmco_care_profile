const form = document.getElementById("ch-details");

form?.addEventListener("submit", (event) => {
	event.preventDefault();
	const saved = form.querySelector(".ch-saved");
	saved.hidden = true;
	frappe.call({
		method: "afmco_care_profile.afmco_care_profile.api.profile.care_profile_set",
		args: Object.fromEntries(new FormData(form)),
		btn: form.querySelector("button"),
		callback: (r) => {
			for (const [fieldname, value] of Object.entries(r.message || {})) {
				if (form.elements[fieldname]) form.elements[fieldname].value = value || "";
			}
			saved.hidden = false;
		},
	});
});
