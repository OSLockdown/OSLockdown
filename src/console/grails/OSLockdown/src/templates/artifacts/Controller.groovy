@artifact.package@class @artifact.name@ {

    def index = { }
    
    /**
     * Clears the flash of all messages that are currently set on it
     */
    private void clearFlash() {
        flash.message = "";
        flash.warning = "";
        flash.error = "";
    }    
}
