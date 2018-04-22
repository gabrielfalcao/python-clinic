// @[?request_data.external_order_id=='GD000013475'] | [0]
import matchAll from 'match-all'


export const join_types = {
    AND: "&",
    OR: "|",
}

export const criteria_to_string = (criteria) => {
    const parts = Object.keys(criteria).map((key) => {
        const value = criteria[key]
        return `${key}: "${value}"`
    })
    return parts.join(' ')
}

export const string_to_criteria = (query) => {
    const criteria = {}
    const regular_expressions = [
        /(([^:\s]+\s*[:]\s*[^:]+)\s*)/g,
        /(([^":\s]+\s*[:]\s*["][^"]+["])\s*)/g,
        /(([^':\s]+\s*[:]\s*['][^']+['])\s*)/g,
        /(([^`:\s]+\s*[:]\s*[`][^`]+[`])\s*)/g,
        /(([^"=\s]+\s*[=]\s*["][^"]+["])\s*)/g,
        /(([^'=\s]+\s*[=]\s*['][^']+['])\s*)/g,
        /(([^`=\s]+\s*[=]\s*[`][^`]+[`])\s*)/g,
    ]
    regular_expressions.forEach((pattern) => {
        matchAll(query, pattern).toArray().forEach((tuple) => {
            const [key, value] = tuple.split(/\s*:\s*/, 2)
            criteria[key] = value
                .replace(/\s*["]\s*/g, '')
                .replace(/\s*[']\s*/g, '')
                .replace(/\s*[`]\s*/g, '')
        })
    })
    return criteria
}
