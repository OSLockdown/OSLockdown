<div class="baselineSection">
  <fieldset>
    <legend><g:fieldValue bean="${baselineSection}" field="name" /></legend>
    <g:each in="${baselineSection?.baselineModules}" var="baselineModule" status="i">
      <g:render template="baselineModule" model="${[baselineModule:baselineModule,i:i,immutable:immutable]}"/>
    </g:each>
  </fieldset>
</div>