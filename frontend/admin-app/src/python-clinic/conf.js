const DEFAULT_BASE_URL = 'https://python.clinic'

function removeLeadingSlash(string) {
    return string.replace(new RegExp('[/]+$'), '')
}

class PythonClinicAdminConfiguration {
    constructor() {
        this.config = this.loadFromWindow()
    }
    loadFromWindow() {
        const config = {...window.PYTHON_CLINIC_CONFIG}
        let BASE_URL = window.PYTHON_CLINIC_API_BASE_URL
        if (!BASE_URL) {
            /* if (window && window.location) {
             *     BASE_URL = window.location.origin
             *     if (BASE_URL === 'http://localhost:3000') {
             *         BASE_URL = 'http://localhost:4242'
             *     }
             * } else {*/
                BASE_URL = DEFAULT_BASE_URL
            /* }*/
        }
        config['base_url'] = removeLeadingSlash(BASE_URL)
        return config
    }
    base_url() {
        const config = this.loadFromWindow()
        const {base_url} = config
        if (base_url && base_url.length > 0) {
            return base_url
        }
        return window.location.origin
    }
    path() {
        const config = this.loadFromWindow()
        const {path} = config
        return path
    }
}

export const config = new PythonClinicAdminConfiguration()
export default PythonClinicAdminConfiguration
