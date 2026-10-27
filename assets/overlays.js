document.body.insertAdjacentHTML("beforeend",`<div class="modal-overlay" id="modalOverlay" aria-hidden="true">
  <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
    <button type="button" class="modal-close" aria-label="Close"><i class="fas fa-times"></i></button>
    <h2 id="modalTitle">Book a private visit</h2>
    <p class="modal-subtitle" id="modalSubtitle">Private consultation</p>
    <div class="form-shell">
<form class="inquiry-form" novalidate data-project="General enquiry">
  <div class="form-row">
    <div class="form-group"><input id="m-name" name="name" type="text" placeholder=" " autocomplete="name" required/><label for="m-name">Full name *</label><span class="field-error" aria-live="polite"></span></div>
    <div class="form-group"><input id="m-phone" name="phone" type="tel" inputmode="tel" placeholder=" " autocomplete="tel" required/><label for="m-phone">Phone *</label><span class="field-error" aria-live="polite"></span></div>
  </div>
  <div class="form-group"><input id="m-email" name="email" type="email" placeholder=" " autocomplete="email"/><label for="m-email">Email (optional)</label><span class="field-error" aria-live="polite"></span></div>
  <div class="form-row">
    <div class="form-group">
      <select id="m-interest" name="interest" data-label="Interested in">
        <option>2 BHK Apartments</option><option selected>3 BHK Apartments</option><option>4 BHK Apartments</option>
        <option>5 BHK &amp; penthouses</option><option>Penthouses</option><option>Villas</option><option>GIFT City \u2014 Residential</option><option>GIFT City \u2014 Commercial</option><option>Offices &amp; showrooms \u2014 Ahmedabad</option><option>Investment advice</option><option>Land in Gujarat \u2014 Buy</option><option>Land in Gujarat \u2014 Sell</option><option>Global property</option>
      </select><label for="m-interest">Interested in</label>
    </div>
    <div class="form-group">
      <select id="m-visit" name="visit" data-label="Preferred visit">
        <option>Weekday morning</option><option>Weekday evening</option><option selected>Weekend</option><option>Video call walkthrough</option>
      </select><label for="m-visit">Preferred visit</label>
    </div>
  </div>
  <div class="form-row">
    <div class="form-group">
      <select id="m-who" name="who" data-label="You are">
        <option>Buying for myself / family</option><option>Investor</option><option>NRI buyer</option><option>Selling my property</option><option>Broker / channel partner</option>
      </select><label for="m-who">You are</label>
    </div>
    <div class="form-group">
      <select id="m-when" name="when" data-label="Plan to buy">
        <option>Within 3 months</option><option>3 \u2013 6 months</option><option>6 \u2013 12 months</option><option>Just exploring</option>
      </select><label for="m-when">Plan to buy</label>
    </div>
  </div>
  <div class="form-group"><textarea id="m-message" name="message" rows="3" placeholder=" "></textarea><label for="m-message">Message (optional)</label></div>
  <div class="form-actions">
    <button type="submit" class="submit-btn wa-submit"><i class="fas fa-paper-plane"></i> <span class="btn-label">Send enquiry</span></button>
  </div>
  <p class="form-note"><i class="fas fa-lock"></i> Your data is secure. We never share your details with anyone without your consent. Every enquiry is checked only to make sure it comes from a genuine buyer, not a fake one. To stop spam, we also note your device type and approximate location with the enquiry.</p>
</form>
<div class="form-success" role="status">
  <i class="fas fa-check-circle"></i><h3>Enquiry sent</h3><p data-s="msg"></p>
  <button type="button" class="cta-btn ghost small" data-form-reset>Start a new enquiry</button>
</div>
</div>
  </div>
</div>

<div class="modal-overlay" id="detailOverlay" aria-hidden="true">
  <div class="modal-content detail-modal" role="dialog" aria-modal="true" aria-labelledby="dName">
    <button type="button" class="modal-close" aria-label="Close"><i class="fas fa-times"></i></button>
    <div class="detail-media"><img data-d="img" alt="" src="data:image/gif;base64,R0lGODlhAQABAAAAACw="/><div class="project-art" data-d="art" hidden aria-hidden="true"><span class="pa-city" data-d="artcity"></span><span class="pa-country" data-d="artcountry"></span></div></div>
    <div class="detail-body">
      <span class="project-category" data-d="cat"></span>
      <h2 id="dName" data-d="name"></h2>
      <p class="project-location"><i class="fas fa-map-marker-alt"></i> <span data-d="loc"></span> <a class="project-map" data-d="map" href="https://www.google.com/maps" target="_blank" rel="noopener noreferrer">View on Google Maps</a></p>
      <p class="project-dev" data-d="devwrap">by <span data-d="dev"></span></p>
      <div class="price" data-d="price"></div><span class="price-label" data-d="plabel"></span>
      <p class="detail-blurb" data-d="blurb"></p>
      <p class="travel-refund" data-d="refund" hidden><i class="fas fa-plane"></i> <span><strong>Travel cost refunded.</strong> Fly out to see it before you buy: when your purchase completes through us, we refund your travel cost for the visit.</span></p>
      <dl class="unit-strip big">
        <div><dt>Total units</dt><dd data-d="total"></dd></div>
        <div><dt>Available</dt><dd data-d="avail"></dd></div>
        <div><dt>Possession</dt><dd data-d="poss"></dd></div>
      </dl>
      <h3 class="detail-h" data-d="mixh">Unit types, sizes and prices</h3>
      <div class="mix-wrap"><table class="mix-table">
        <thead><tr><th scope="col">Unit type</th><th scope="col">Size</th><th scope="col" data-d="pth">Price</th><th scope="col">Available</th></tr></thead>
        <tbody data-d="mix"></tbody>
      </table></div>
      <div class="detail-specs">
        <div class="wide"><small>Overall size range</small><strong data-d="size"></strong></div>
        <div class="wide" data-d="buildwrap"><small>Project</small><strong data-d="build"></strong></div>
        <div class="wide"><small data-d="reglabel">RERA</small><strong data-d="rera" style="font-size:.8rem;word-break:break-word"></strong></div>
      </div>
      <p class="detail-source">Source: <span data-d="source"></span>. <span data-d="srcnote">Prices and availability change; we confirm both before you book.</span></p>
      <div class="btn-row">
        <button type="button" class="cta-btn primary" data-d="enquire"><i class="fas fa-calendar-alt"></i> Enquire</button>
        <a class="cta-btn wa" data-d="wa" href="#" target="_blank" rel="noopener noreferrer"><i class="fab fa-whatsapp"></i> WhatsApp</a>
      </div>
      <a class="cta-btn ghost" data-d="page" href="projects.html" style="width:100%;margin-top:12px"><i class="fas fa-file-lines"></i> Open the full project page</a>
      <a class="cta-btn ghost" data-d="3d" href="shantigram.html#explorer" style="width:100%;margin-top:12px"><i class="fas fa-cube"></i> See it in the 3D township</a>
    </div>
  </div>
</div>`);
