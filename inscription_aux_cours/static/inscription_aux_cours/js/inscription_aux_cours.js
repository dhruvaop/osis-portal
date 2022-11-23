document.addEventListener('DOMContentLoaded', function () {
    addTriggerForFormsEnrollToCourse(getInscrireAuCoursUrl(), getCSRFToken());
    addTriggerForFormsUnenrollToCourse(getDesinscrireAuCoursUrl(), getCSRFToken());
    // addHtmxIndicatorOnForms();

}, false);

function addHtmxIndicatorOnForms() {
    const forms = document.querySelectorAll(".formulaire-inscription-cours")
    forms.forEach((form, key, parent) => {
        const checkBox = form.querySelector("input[type=checkbox]");
        form.setAttribute("htmx-indicator", `#${checkBox.id}`)
    });
}

function getInscrireAuCoursUrl() {
    if (document.querySelector(".panel-formulaires-inscription-cours") !== null) {
        return document.querySelector(".panel-formulaires-inscription-cours").dataset.urlInscrireCours;
    }
    return ""
}

function getDesinscrireAuCoursUrl() {
    if (document.querySelector(".panel-formulaires-inscription-cours") !== null) {
        return document.querySelector(".panel-formulaires-inscription-cours").dataset.urlDesinscrireCours;
    }
    return ""
}

function getCSRFToken() {
    if (document.querySelector(".panel-formulaires-inscription-cours") !== null) {
        return document.querySelector(".panel-formulaires-inscription-cours").dataset.csrfToken;
    }
    return ""
}

function addTriggerForFormsEnrollToCourse(postUrl, csrfToken) {
    const forms = document.querySelectorAll(".formulaire-inscription-cours[data-est-inscrit='False']")
    forms.forEach((value, key, parent) => {
        addTriggerOnForm(value, postUrl, csrfToken)
    });
}

function addTriggerForFormsUnenrollToCourse(postUrl, csrfToken) {
    const forms = document.querySelectorAll(".formulaire-inscription-cours[data-est-inscrit='True']")
    forms.forEach((value, key, parent) => {
        addTriggerOnForm(value, postUrl, csrfToken)
    });
}

function addTriggerOnForm(formElement, postUrl, csrfToken) {
    const codeCours = formElement.dataset.codeCours;
    const codeMiniFormation = formElement.dataset.codeMiniFormation;
    const target = `#form-inscription-${codeMiniFormation}-${ codeCours }`

    triggerHtmxPostOnClick(
        formElement,
        postUrl,
        target,
        {'code_mini_formation': codeMiniFormation, 'code_cours': codeCours},
        {"X-CSRFToken": csrfToken}
    )
}

function triggerHtmxPostOnClick(e, postUrl, target, values, headers) {
    e.addEventListener('click', (event) => {
       htmx.ajax('POST', postUrl, {'target': target, 'swap': 'outerHTML', 'values': values, 'headers': headers})
    });
}
