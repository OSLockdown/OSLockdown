<%@page defaultCodec="none" %>
<g:if test="${warningBanner}">
  <div class="info" style="width: 40%; margin: 2em  auto;">
    <div class="info_header">Warning</div>
    <div class="loginBanner pad5all">${warningBanner}</div>
  </div>
</g:if>
