
<!-- ********************************************************** -->
<!-- ACTION BAR -->
<!-- ********************************************************** -->

<div id="actionbar">

  <g:form>
    <input type="hidden" name="id" value="${processorInstance?.id}" />
    <!--input type="hidden" name="group_id" value="${groupInstance?.id}" /-->
    <!-- How to handle both Processors and Groups with this template? -->

    <shiro:hasAnyRole in="['Administrator','User']">
      <div class="actions">
        <div class="action_title">Processor</div>
        <ui>
          <li><g:actionSubmit class="action_bar_btn" title="Edit" value="Edit" action="edit" id="${processorInstance.id}"/></li>
          <li><g:actionSubmit class="action_bar_btninput" onclick="return confirm('Are you sure you want to delete this processor?');" title="Delete" value="Delete" action="delete" id="${processorInstance.id}"/></li>

        </ui>
      </div>
    </shiro:hasAnyRole>
   </g:form>

</div><!-- navbar -->
