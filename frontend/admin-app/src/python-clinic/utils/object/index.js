import _ from 'lodash'

export class ObjectHelper {
    static key_paths({...obj}) {
        const items = Object.keys(obj).map((key)=>{
            const value = obj[key]
            if (typeof value === 'object') {
                return ObjectHelper.key_paths(value).map((subkey)=> (`${key}.${subkey}`))
            }
            return [key]
        })
        return _.flatten(items)
    }
}

export default ObjectHelper
