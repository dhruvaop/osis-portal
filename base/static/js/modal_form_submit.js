function redirect_after_success(modal, xhr) {
    $(modal).modal('toggle');
    if (xhr.hasOwnProperty('success_url')) {
        window.location.href = xhr["success_url"];
    }
    else {
        window.location.reload();
    }
}

var formAjaxSubmit = function (form, modal) {
    $(form).submit(function (e) {
        // Added preventDefaut so as to not add anchor "href" to address bar
        e.preventDefault();

        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            context: this,
            success: function (xhr, ajaxOptions, thrownError) {
                //Stay on the form if there are errors.
                if ($(xhr).find('.has-error').length > 0) {
                    $(modal).find('.modal-content').html(xhr);
                    // Add compatibility with ckeditor and related textareas
                    bindTextArea();
                    formAjaxSubmit(form, modal);
                    this.dispatchEvent(new CustomEvent("formAjaxSubmit:error", {}));
                } else {
                    redirect_after_success(modal, xhr);
                    this.dispatchEvent(new CustomEvent("formAjaxSubmit:success", {}));
                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                // handle response errors here
                this.dispatchEvent(new CustomEvent("formAjaxSubmit:error", {}));
            }
        });
    });
};


// CKEDITOR needs to dynamically bind the textareas during an XMLHttpRequest requests
function bindTextArea() {
    $("textarea[data-type='ckeditortype']").each(function () {
        CKEDITOR.replace($(this).attr('id'), $(this).data('config'));
    });
}

// Before submitting, we need to update textarea with ckeditor element.
function CKupdate() {
    for (let instance in CKEDITOR.instances)
        CKEDITOR.instances[instance].updateElement();
}


$(".trigger_modal").click(function () {
    let url = $(this).data("url");
    let modal_class = $(this).data("modal_class");
    $('#modal_dialog_id').attr("class", "modal-dialog").addClass(modal_class);
    $('#form-ajax-modal').modal('toggle');

    $('#form-modal-ajax-content').load(url, function () {
        bindTextArea();
        formAjaxSubmit('#form-modal-body form', '#form-ajax-modal');
    });
});
