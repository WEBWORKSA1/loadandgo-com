/* LoadandGo.com site settings. Safe to edit.
   The inbox for every form is stored encoded and is only assembled in the browser at the
   moment a form is sent, so it never appears in any page. Regenerate with scripts/encode_inbox.py. */
window.LG_CONFIG = {
  site: "LoadandGo.com",
  _k: [154, 146, 41, 192, 204, 53, 107, 116, 196],
  _v: [237, 248, 77, 186, 167, 76, 6, 7, 166, 173, 213, 82, 178, 179, 92, 8, 92, 170, 249, 260],
  relay: "https://formsubmit.co/ajax/",

  // Optional payment links for the Support page. Leave empty to collect pledges by form
  // (you then reply with a payment link). Paste a full https:// URL to show a pay button.
  payments: {
    paypal: "",       // e.g. https://www.paypal.com/donate/?hosted_button_id=XXXX
    stripe: "",       // e.g. https://buy.stripe.com/XXXX
    kofi: "",         // e.g. https://ko-fi.com/yourname
    buymeacoffee: ""  // e.g. https://buymeacoffee.com/yourname
  },

  // Shown on /contests/. Edit when a sponsor or the support fund confirms a prize.
  contestPrize: "This month's prize is announced here once the support fund or a sponsor confirms it."
};
