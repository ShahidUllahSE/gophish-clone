(function ($, CKEDITOR, Swal, moment) {
    var pages = [];

    function save() {
        const pageId = $("#page_id").val(); // Use hidden input to determine if it's an update
        const pageData = {
            name: $("#name").val(),
            html: CKEDITOR.instances.html_editor.getData(),
            capture_credentials: $("#capture_credentials_checkbox").prop("checked"),
            capture_passwords: $("#capture_passwords_checkbox").prop("checked"),
            collect_emails: $("#collect_emails_checkbox").prop("checked"),
            geolocation_tracking: $("#geolocation_tracking_checkbox").prop("checked"),
            redirect_url: $("#redirect_url_input").val(),
        };

        if (!pageData.name || !pageData.html) {
            Swal.fire("Error", "Title and content are required!", "error");
            return;
        }

        // Determine the correct endpoint
        const url = pageId
            ? `/edit_landing_page/${pageId}/` // Edit page endpoint
            : `/save_landing_page/`; // New page endpoint
        const method = "POST";

        $.ajax({
            url: url,
            method: method,
            contentType: "application/json",
            data: JSON.stringify(pageData),
            headers: { "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val() },
            success: function () {
                Swal.fire(
                    "Success",
                    pageId ? "Page updated successfully!" : "Page created successfully!",
                    "success"
                );
                loadPages(); // Reload the table
                dismissModal(); // Clear and close the modal
            },
            error: function (err) {
                Swal.fire("Error", err.responseJSON?.error || "An error occurred.", "error");
            },
        });
    }

    function dismissModal() {
        $("#page_id").val(""); // Clear the hidden page ID
        $("#name").val("");
        CKEDITOR.instances.html_editor.setData("");
        $("#redirect_url_input").val("");
        $("#modal").find("input[type='checkbox']").prop("checked", false);
        $("#capture_passwords").hide();
        $("#redirect_url").hide();
        $("#modal").modal("hide");
    }

    function edit(pageIndex) {
        const pageData = pages[pageIndex];
        $("#modalLabel").text("Edit Landing Page");
        $("#page_id").val(pageData.id); // Set the hidden ID for editing
        $("#name").val(pageData.name);
        CKEDITOR.instances.html_editor.setData(pageData.html);
        $("#capture_credentials_checkbox").prop("checked", pageData.capture_credentials);
        $("#capture_passwords_checkbox").prop("checked", pageData.capture_passwords);
        $("#collect_emails_checkbox").prop("checked", pageData.collect_emails);
        $("#geolocation_tracking_checkbox").prop("checked", pageData.geolocation_tracking);
        $("#redirect_url_input").val(pageData.redirect_url);

        if (pageData.capture_credentials) {
            $("#capture_passwords").show();
            $("#redirect_url").show();
        }

        $("#modalSubmit").off("click").click(save); // Rebind save function
        $("#modal").modal("show");
    }

    function deletePage(pageIndex) {
        const pageData = pages[pageIndex];

        Swal.fire({
            title: "Are you sure?",
            text: "This action cannot be undone.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Yes, delete it!",
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `/delete_landing_page/${pageData.id}/`,
                    method: "DELETE",
                    headers: { "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val() },
                    success: function () {
                        Swal.fire("Deleted!", "The page has been deleted.", "success");
                        loadPages(); // Reload pages
                    },
                    error: function (err) {
                        Swal.fire("Error", err.responseJSON?.error || "An error occurred.", "error");
                    },
                });
            }
        });
    }

    function loadPages() {
        $("#pagesTable").hide();
        $("#emptyMessage").hide();
        $("#loading").show();

        $.ajax({
            url: `/get_landing_pages/`, // Ensure this endpoint is implemented
            method: "GET",
            success: function (data) {
                pages = data;
                $("#loading").hide();

                if (pages.length > 0) {
                    $("#pagesTable").show();
                    const pagesTable = $("#pagesTable").DataTable({
                        destroy: true,
                        columnDefs: [{ orderable: false, targets: "no-sort" }],
                    });
                    pagesTable.clear();

                    const rows = pages.map((page, index) => [
                        escapeHtml(page.name),
                        moment(page.modified_date).format("MMMM Do YYYY, h:mm:ss a"),
                        `<div class='pull-right'>
                            <button class='btn btn-primary' title='Edit Page' onclick='edit(${index})'>
                                <i class='fa fa-pencil'></i>
                            </button>
                            <button class='btn btn-danger' title='Delete Page' onclick='deletePage(${index})'>
                                <i class='fa fa-trash-o'></i>
                            </button>
                        </div>`,
                    ]);

                    pagesTable.rows.add(rows).draw();
                } else {
                    $("#emptyMessage").show();
                }
            },
            error: function () {
                $("#loading").hide();
                Swal.fire("Error", "Error fetching pages.", "error");
            },
        });
    }

    function importSite() {
        const siteUrl = $("#import_url").val();

        if (!siteUrl) {
            Swal.fire("Error", "Please enter a valid URL!", "error");
            return;
        }

        $.ajax({
            url: `/import_site/`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ site_url: siteUrl }),
            headers: { "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val() },
            success: function (response) {
                CKEDITOR.instances.html_editor.setData(response.content);
                $("#importModal").modal("hide");
                Swal.fire("Success", "Site imported successfully!", "success");
            },
            error: function (err) {
                Swal.fire("Error", err.responseJSON?.error || "Failed to import the site.", "error");
            },
        });
    }

    function previewImportedSite() {
        const content = CKEDITOR.instances.html_editor.getData();

        if (!content) {
            Swal.fire("Error", "No content available for preview.", "error");
            return;
        }

        $.ajax({
            url: `/preview_imported_site/`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ content }),
            headers: { "X-CSRFToken": $("input[name='csrfmiddlewaretoken']").val() },
            success: function (response) {
                const previewWindow = window.open("", "_blank");
                previewWindow.document.write(response);
                previewWindow.document.close();
            },
            error: function (err) {
                Swal.fire("Error", err.responseJSON?.error || "Failed to preview the content.", "error");
            },
        });
    }

    $(document).ready(function () {
        $(".modal").on("hidden.bs.modal", dismissModal);

        $("#capture_credentials_checkbox").change(function () {
            $("#capture_passwords").toggle();
            $("#redirect_url").toggle();
        });

        $("#importSubmit").click(importSite); // Bind import function
        $("#previewImported").click(previewImportedSite); // Bind preview function
        loadPages(); // Initial load of pages
    });
})(jQuery, CKEDITOR, Swal, moment);
