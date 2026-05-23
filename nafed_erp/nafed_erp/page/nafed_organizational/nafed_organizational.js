let company_field;
// const checkmap = {};

frappe.pages['nafed-organizational'].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Organizational Chart',
		single_column: true
	});
	//   document.body.style.overflow = "hidden";

	frappe.router.on("change", toggleBodyScrollForOrgChart);

	//   style="

	// background: #0f766e;
	//  "
	$(page.body).append(`
  <div id="org-chart-viewport"
    style="
      position: relative;
      width: 100%;
      height: calc(100vh - 140px);
      overflow-x: auto;
      overflow-y: auto;
    "
  >
    <div id="org-chart-canvas"
      style="
        position: relative;
        display: inline-block;
        min-width: max-content;
        min-height: max-content;
        padding: 80px;
      "
    >
      <svg id="org-lines"
        style="
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          z-index: 1;
        "
      ></svg>

      <div id="vishal-children-container"
        style="
          position: relative;
          z-index: 2;
          display: flex;
          flex-direction: column;
          gap: 50px;
        "
      ></div>
    </div>
  </div>
`);


	company_field = page.add_field({
		fieldtype: "Link",
		fieldname: "company",
		label: "Company",
		options: "Company",
		change() {
			load_root(company_field.get_value());
			toggleBodyScrollForOrgChart();

		}
	});

	//   page.set_primary_action("Expand All", () => {
	//     expandAllCustom();
	//   });

	const def = frappe.defaults.get_default("company");
	if (def) {
		company_field.set_value(def);
		load_root(def);
	}
};

function toggleBodyScrollForOrgChart() {
	const route = frappe.get_route_str();

	if (route === "nafed-organizational") {
		document.body.style.overflow = "hidden";
	} else {
		document.body.style.overflow = "";
	}
}



function load_root(company) {
	frappe.call({
		method: "nafed_erp.hire_to_retire.doc_events.org_chart.get_children",
		args: { company },
		callback(r) {
			$("#vishal-children-container").empty();
			render_row(r.message, 0);

			//   setTimeout(drawAllLines, 80);
		}
	});
}

function render_row(nodes, level, parent_uid = "") {
	const row = $(`
  <div class="org-row"
    style="
      display: flex;
      width: max-content;
    "
  >
    <div class="org-row-inner"
      style="
        display: flex;
        gap: 24px;
      "
    ></div>
  </div>
`);


	nodes.forEach(emp => {
		const node_uid = `${parent_uid || 'root'}__${emp.id}__${level}`;

		const base_url = window.location.origin;
		const avatar_img = emp.image
			? `${base_url}${emp.image}`
			: `${base_url}/assets/frappe/images/default-avatar.png`;
		row.find(".org-row-inner").append(`
      <div class="vishal-org-node"
        data-id="${emp.id}"
  data-node-uid="${node_uid}"
  data-parent-uid="${parent_uid}"
  data-level="${level}"
  data-connections="${emp.connections || 0}"
        style="
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;
          min-width: 260px;
          padding: 14px 16px;
          background: #ffffff;
          border: 1px solid #e5e7eb;
          border-radius: 12px;
          cursor: pointer;
          position: relative;
          z-index: 3;
          box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        "
      >

        <div style="
          width: 36px;
          height: 36px;
          background: #f3f4f6;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          border: 1px solid #e5e7eb;
        ">
          <img src="${avatar_img}"
            style="
              width: 100%;
              height: 100%;
              object-fit: cover;
              display: block;
            "
          />
        </div>

        <div>
          <div class="org-name" style="font-weight: 600;">
            ${emp.name}
          </div>

          ${emp.department ? `<div class="org-subtext" style="font-size:12px;color:#6b7280;">${emp.department}</div>` : ""}
          ${emp.title ? `<div class="org-subtext" style="font-size:12px;color:#6b7280;">${emp.title}</div>` : ""}
          ${emp.grade ? `<div class="org-subtext" style="font-size:12px;color:#6b7280;">${emp.grade}</div>` : ""}

          <div class="org-subtext" style="font-size:12px;color:#6b7280;">
            ${emp.connections || 0} Connections
          </div>
        </div>

        <a href="/app/employee/${emp.id}"
          target="_blank"
          onclick="event.stopPropagation()"
          style="
            padding: 6px 10px;
            background: #f3f4f6;
            border-radius: 6px;
            font-size: 12px;
            color: #374151;
            text-decoration: none;
          "
        >
          Edit
        </a>

      </div>
    `);
	});

	$("#vishal-children-container").append(row);
}



$(document).on("click", ".vishal-org-node", function () {

	if (this.dataset.connections === "0") return;

	setSelectedNodeInline(this);

	const level = +this.dataset.level;
	const parentNodeUid = this.dataset.nodeUid;
	const empId = this.dataset.id;

	$(".org-row").filter(function () {
		return +$(this).find(".vishal-org-node").data("level") > level;
	}).remove();

	frappe.call({
		method: "nafed_erp.hire_to_retire.doc_events.org_chart.get_children",
		args: {
			company: company_field.get_value(),
			parent: empId
		},
		callback(r) {
			if (!r.message?.length) return;

			render_row(r.message, level + 1, parentNodeUid);
			setTimeout(drawAllLines, 80);
		}
	});
});


function setSelectedNodeInline(selectedEl) {
	document.querySelectorAll(".vishal-org-node").forEach(el => {
		el.style.background = "#ffffff";
		el.style.borderColor = "#e5e7eb";

		const name = el.querySelector(".org-name");
		const sub = el.querySelector(".org-subtext");
		const edit = el.querySelector(".vishal-btn");

		if (name) name.style.color = "#111827";     // normal text
		if (sub) sub.style.color = "#6b7280";       // normal subtext
		if (edit) {
			edit.style.background = "#f3f4f6";
			edit.style.color = "#374151";
		}
	});

	selectedEl.style.background = "#f9fafb";     // light selected bg
	selectedEl.style.borderColor = "#9ca3af";    // visible border

	const name = selectedEl.querySelector(".org-name");
	const sub = selectedEl.querySelector(".org-subtext");
	const edit = selectedEl.querySelector(".vishal-btn");

	if (name) name.style.color = "#111827";       // dark title
	if (sub) sub.style.color = "#374151";         // darker subtext
	if (edit) {
		edit.style.background = "#e5e7eb";
		edit.style.color = "#111827";
	}
}





function getNodeCenter(el) {
	const canvas = document.getElementById("org-chart-canvas");

	const nodeRect = el.getBoundingClientRect();
	const canvasRect = canvas.getBoundingClientRect();

	return {
		x: nodeRect.left + nodeRect.width / 2 - canvasRect.left,
		y: nodeRect.top + nodeRect.height / 2 - canvasRect.top
	};
}


function drawVerticalPath(from, to) {
	const midY = (from.y + to.y) / 2;

	return `
    <path
      d="
        M ${from.x} ${from.y}
        V ${midY}
        H ${to.x}
        V ${to.y}
      "
      stroke="#ccc"
      stroke-width="2"
      fill="none"
    />
  `;
}

function drawAllLines() {
	const svg = document.getElementById("org-lines");
	const canvas = document.getElementById("org-chart-canvas");

	svg.innerHTML = "";

	const width = canvas.scrollWidth;
	const height = canvas.scrollHeight;

	svg.setAttribute("width", width);
	svg.setAttribute("height", height);
	svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

	const nodes = document.querySelectorAll(".vishal-org-node");

	nodes.forEach(node => {
		const parentUid = node.dataset.parentUid;
		if (!parentUid) return;

		const parentNode = document.querySelector(
			`.vishal-org-node[data-node-uid="${parentUid}"]`
		);
		if (!parentNode) return;

		svg.innerHTML += drawVerticalPath(
			getNodeCenter(parentNode),
			getNodeCenter(node)
		);
	});
}



// expandAllCustom

function expandAllCustom() {
	frappe.call({
		method: "nafed_erp.hire_to_retire.doc_events.org_chart.get_children_expand_all",
		args: {
			company: company_field.get_value()
		},
		callback(r) {
			if (!r.message) return;

			$("#vishal-children-container").empty();
			renderRecursive(r.message, 0, "");
			setTimeout(drawAllLines, 150);
		}
	});
}


function renderRecursive(nodes, level, parent_id) {
	if (!nodes || !nodes.length) return;

	render_row(nodes, level, parent_id);

	nodes.forEach(n => {
		if (n.children && n.children.length) {
			renderRecursive(n.children, level + 1, n.id);
		}
	});
}


