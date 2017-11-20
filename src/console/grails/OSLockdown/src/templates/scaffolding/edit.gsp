<% import org.codehaus.groovy.grails.orm.hibernate.support.ClosureEventTriggeringInterceptor as Events %>
<%=packageName%>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="layout" content="main" />
        <title><g:message code="${domainClass.propertyName}.edit" default="Edit ${className}" /></title>
    </head>
    <body>
        <div class="nav">
            <span class="menuButton"><a class="home" href="\${createLinkTo(dir: '')}"><g:message code="home" default="Home" /></a></span>
            <span class="menuButton"><g:link class="list" action="list"><g:message code="${domainClass.propertyName}.list" default="${className} List" /></g:link></span>
            <span class="menuButton"><g:link class="create" action="create"><g:message code="${domainClass.propertyName}.new" default="New ${className}" /></g:link></span>
        </div>
        <div class="body">
            <h1><g:message code="${domainClass.propertyName}.edit" default="Edit ${className}" /></h1>
            <g:if test="\${flash.message}">
            <div class="message"><g:message code="\${flash.message}" args="\${flash.args}" default="\${flash.defaultMessage}" /></div>
            </g:if>
            <g:hasErrors bean="\${${propertyName}}">
            <div class="errors">
                <g:renderErrors bean="\${${propertyName}}" as="list" />
            </div>
            </g:hasErrors>
            <g:form method="post" <%= multiPart ? " enctype=\"multipart/form-data\"" : "" %>>
                <g:hiddenField name="id" value="\${${propertyName}?.id}" />
                <g:hiddenField name="version" value="\${${propertyName}?.version}" />
                <div class="dialog">
                    <table>
                        <tbody>
                        <%  excludedProps = ["version",
                                             "id",
                                             Events.ONLOAD_EVENT,
                                             Events.BEFORE_INSERT_EVENT,
                                             Events.BEFORE_UPDATE_EVENT,
                                             Events.BEFORE_DELETE_EVENT]
                            props = domainClass.properties.findAll { !excludedProps.contains(it.name) }
                            Collections.sort(props, comparator.constructors[0].newInstance([domainClass] as Object[]))
                            props.each { p ->
                                cp = domainClass.constrainedProperties[p.name]
                                display = (cp ? cp.display : true)
                                if (display) { %>
                            <tr class="prop">
                                <td valign="top" class="name">
                                    <label for="${p.name}"><g:message code="${domainClass.propertyName}.${p.name}" default="${p.naturalName}" />:</label>
                                </td>
                                <td valign="top" class="value \${hasErrors(bean: ${propertyName}, field: '${p.name}', 'errors')}">
                                    ${renderEditor(p)}
                                </td>
                            </tr>
                        <%  }   } %>
                        </tbody>
                    </table>
                </div>
                <div class="buttons">
                    <span class="button"><g:actionSubmit class="save" action="update" value="\${message(code: 'update', 'default': 'Update')}" /></span>
                    <span class="button"><g:actionSubmit class="delete" action="delete" value="\${message(code: 'delete', 'default': 'Delete')}" onclick="return confirm('\${message(code: 'delete.confirm', 'default': 'Are you sure?')}');" /></span>
                </div>
            </g:form>
        </div>
    </body>
</html>
