/*
 * Original file generated in 2009 by Grails v1.1.1 under the Apache 2 License.
 * Modifications are Copyright 2009-2010 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'ApacheV2_LICENSE.txt' at the root of the source tree for the full Apache V2 license, or
 * visit http://apache.org/licenses/LICENSE-2.0.html instead.
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
<%=packageName ? "package ${packageName}\n\n" : ""%>class ${className}Controller {

    def index = { redirect(action: "list", params: params) }

    // the delete, save and update actions only accept POST requests
    static allowedMethods = [save: "POST", update: "POST", delete: "POST"]

    def list = {
        params.max = Math.min(params.max ? params.max.toInteger() : 10,  100)
        [${propertyName}List: ${className}.list(params), ${propertyName}Total: ${className}.count()]
    }

    def create = {
        def ${propertyName} = new ${className}()
        ${propertyName}.properties = params
        return [${propertyName}: ${propertyName}]
    }

    def save = {
        def ${propertyName} = new ${className}(params)
        if (!${propertyName}.hasErrors() && ${propertyName}.save()) {
            flash.message = "${domainClass.propertyName}.created"
            flash.args = [${propertyName}.id]
            flash.defaultMessage = "${className} \${${propertyName}.id} created"
            redirect(action: "show", id: ${propertyName}.id)
        }
        else {
            render(view: "create", model: [${propertyName}: ${propertyName}])
        }
    }

    def show = {
        def ${propertyName} = ${className}.get(params.id)
        if (!${propertyName}) {
            flash.message = "${domainClass.propertyName}.not.found"
            flash.args = [params.id]
            flash.defaultMessage = "${className} not found with id \${params.id}"
            redirect(action: "list")
        }
        else {
            return [${propertyName}: ${propertyName}]
        }
    }

    def edit = {
        def ${propertyName} = ${className}.get(params.id)
        if (!${propertyName}) {
            flash.message = "${domainClass.propertyName}.not.found"
            flash.args = [params.id]
            flash.defaultMessage = "${className} not found with id \${params.id}"
            redirect(action: "list")
        }
        else {
            return [${propertyName}: ${propertyName}]
        }
    }

    def update = {
        def ${propertyName} = ${className}.get(params.id)
        if (${propertyName}) {
            if (params.version) {
                def version = params.version.toLong()
                if (${propertyName}.version > version) {
                    <%  def lowerCaseName = grails.util.GrailsNameUtils.getPropertyName(className) %>
                    ${propertyName}.errors.rejectValue("version", "${lowerCaseName}.optimistic.locking.failure", "Another user has updated this ${className} while you were editing")
                    render(view: "edit", model: [${propertyName}: ${propertyName}])
                    return
                }
            }
            ${propertyName}.properties = params
            if (!${propertyName}.hasErrors() && ${propertyName}.save()) {
                flash.message = "${domainClass.propertyName}.updated"
                flash.args = [params.id]
                flash.defaultMessage = "${className} \${params.id} updated"
                redirect(action: "show", id: ${propertyName}.id)
            }
            else {
                render(view: "edit", model: [${propertyName}: ${propertyName}])
            }
        }
        else {
            flash.message = "${domainClass.propertyName}.not.found"
            flash.args = [params.id]
            flash.defaultMessage = "${className} not found with id \${params.id}"
            redirect(action: "edit", id: params.id)
        }
    }

    def delete = {
        def ${propertyName} = ${className}.get(params.id)
        if (${propertyName}) {
            try {
                ${propertyName}.delete()
                flash.message = "${domainClass.propertyName}.deleted"
                flash.args = [params.id]
                flash.defaultMessage = "${className} \${params.id} deleted"
                redirect(action: "list")
            }
            catch (org.springframework.dao.DataIntegrityViolationException e) {
                flash.message = "${domainClass.propertyName}.not.deleted"
                flash.args = [params.id]
                flash.defaultMessage = "${className} \${params.id} could not be deleted"
                redirect(action: "show", id: params.id)
            }
        }
        else {
            flash.message = "${domainClass.propertyName}.not.found"
            flash.args = [params.id]
            flash.defaultMessage = "${className} not found with id \${params.id}"
            redirect(action: "list")
        }
    }
}
