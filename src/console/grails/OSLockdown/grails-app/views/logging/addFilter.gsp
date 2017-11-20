<%@page contentType="text/xml"%>
 
<taconite-root xml:space="preserve">
    <g:set var="filterCount" value="${Integer.parseInt(params.filterCount) + 1 }" />
    <g:if test="${params.filterType == 'user'}">
        <taconite-append-as-children contextNodeID="userFilters">
            <div class="pad3top" id="div.filter.${filterCount}" filter="user">                
                <a class="btn" href="javascript:removeFilter('user','${filterCount}');">-</a>
                <g:select class="paddedSelect" name="user" from="${dataSet}" optionKey="username" optionValue="username"/>
            </div>
        </taconite-append-as-children>     
    </g:if>
    <g:elseif test="${params.filterType == 'action'}">
        <taconite-append-as-children contextNodeID="actionFilters">
            <div class="pad3top" id="div.filter.${filterCount}" filter="action">                
                <a class="btn" href="javascript:removeFilter('action','${filterCount}');">-</a>
                <g:select class="paddedSelect" name="action" from="${dataSet}"/>
            </div>
        </taconite-append-as-children>    
    </g:elseif>
    <g:elseif test="${params.filterType == 'profile'}">
        <taconite-append-as-children contextNodeID="profileFilters">
            <div class="pad3top" id="div.filter.${filterCount}" filter="profile">                
                <a class="btn" href="javascript:removeFilter('profile','${filterCount}');">-</a>
                <g:select class="paddedSelect" name="profile" from="${dataSet}" optionKey="name" optionValue="name"/>
            </div>
        </taconite-append-as-children>     
    </g:elseif>    
    <g:elseif test="${params.filterType == 'group'}">
        <taconite-append-as-children contextNodeID="groupFilters">
            <div class="pad3top" id="div.filter.${filterCount}" filter="group">                
                <a class="btn" href="javascript:removeFilter('group','${filterCount}');">-</a>
                <g:select class="paddedSelect" name="group" from="${dataSet}" optionKey="name" optionValue="name"/>
            </div>
        </taconite-append-as-children>    
    </g:elseif>
    <g:elseif test="${params.filterType == 'client'}">
        <taconite-append-as-children contextNodeID="clientFilters">
            <div class="pad3top" id="div.filter.${filterCount}" filter="client">                
                <a class="btn" href="javascript:removeFilter('client','${filterCount}');">-</a>
                <g:select class="paddedSelect" name="client" from="${dataSet}" optionKey="name" optionValue="name"/>
            </div>
        </taconite-append-as-children>    
    </g:elseif>
    <g:elseif test="${params.filterType == 'word'}">
        <taconite-append-as-children contextNodeID="wordFilters">
            <div class="pad3top" id="div.filter.${filterCount}" filter="word">                
                <a class="btn" href="javascript:removeFilter('word','${filterCount}');">-</a>
                <g:textField name="word" size="20"/>                             
            </div>
        </taconite-append-as-children>            
    </g:elseif>
    <g:elseif test="${params.filterType == 'module'}">
        <taconite-append-as-children contextNodeID="moduleFilters">
            <div class="pad3top" id="div.filter.${filterCount}" filter="module">                
                <a class="btn" href="javascript:removeFilter('module','${filterCount}');">-</a>
                <g:select class="paddedSelect" name="module" from="${dataSet}" optionKey="library" optionValue="name" value="${params.module}"/>
            </div>
        </taconite-append-as-children>            
    </g:elseif>    
    
    <!-- Set the hidden count to the latest value -->                       
    <taconite-set-attributes matchMode="plain" contextNodeID="filterCount" value="${filterCount}" />    
</taconite-root>