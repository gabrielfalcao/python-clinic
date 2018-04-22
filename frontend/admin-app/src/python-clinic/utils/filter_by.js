const get_matched_criteria_from_item = (item, criteria) => {
    return Object.keys(criteria).map((key) => {
        let expected = null;
        try {
            expected = new RegExp(criteria[key], 'ig')
        } catch (e) {
            console.error(`invalid regex: ${criteria[key]}`, e)
            return null
        }

        let value = {...item}
        key.split('.').forEach((level) => {
            if (typeof value !== 'object') {
                console.log('oops')
                return
            }
            value = value[level]
        })
        if (!value) {
            return null
        }
        const matched = value.match(expected)
        if (!matched) {
            return null
        }
        return matched
    }).filter((o) => o !== null)
}

const item_matches_any_criteria = (item, criteria) => {
    const matched = Object.values(get_matched_criteria_from_item(item, criteria))
    return matched.length > 0
}
const item_matches_all_criteria = (item, criteria) => {
    const matched = Object.values(get_matched_criteria_from_item(item, criteria))
    return matched.length === Object.keys(criteria).length
}

export class FilterBy {
    static any(items, {...criteria}) {
        return items.filter((item) => item_matches_any_criteria(item, criteria))
    }
    static all(items, {...criteria}) {
        return items.filter((item) => item_matches_all_criteria(item, criteria))
    }
}

export default FilterBy
