const contactForm =
    document.getElementById("contactForm");

const formMessage =
    document.getElementById("formMessage");


contactForm.addEventListener("submit", function(event) {

    event.preventDefault();

    const name =
        document.getElementById("name").value;

    formMessage.textContent =
        `Thank you ${name}! Your message has been received.`;

    contactForm.reset();

});