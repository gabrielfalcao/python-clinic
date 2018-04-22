import _ from 'lodash'
import './QueryInput.css'
import React from "react"
import PropTypes from 'prop-types'
import Autosuggest from 'react-autosuggest';

import * as utils from 'python-clinic/utils'


class QueryInput extends React.Component {
    state = {
        value: '',
        suggestions: []
    };

    static propTypes = {
        projects: PropTypes.array.isRequired,
        onTypeQuery: PropTypes.func.isRequired,
        placeholder: PropTypes.string,
        defaultValue: PropTypes.string,
    }

    onChange = (event, { newValue, method }) => {
        this.setState({
            value: newValue
        });
    }

    onSuggestionsFetchRequested = ({ value }) => {
        this.setState({
            suggestions: this.getSuggestions(value)
        });
    }

    onSuggestionsClearRequested = () => {
        this.setState({
            suggestions: []
        });
    }

    field_names_matching = (name) => {
        const {projects} = this.props
        if (projects.length < 1) {
            return []
        }
        let regex
        try {
            regex = new RegExp(name)
        } catch (e) {
            return []
        }
        const sample = projects[0]
        const field_names = utils.object.key_paths(sample)
        return field_names.filter((field_name)=>{
            return field_name.match(regex)
        })
    }
    getFieldNameSuggestions = (value) => {
        const matching_fields = this.field_names_matching(value)
        const suggestions = matching_fields.map((name) => ({
            field: name,
            original: value,
            query: `${name}: `,
            value: `${name}: `,
        }))
        return (suggestions.length > 0) ? suggestions : null
    }
    getValueSuggestions = (value) => {
        const {projects} = this.props
        const matched = value.match(/^(.*)[:]\s*([^'"]*)$/)
        if (!matched) {
            return null
        }
        const field_name = matched[1]
        const field_value = matched[2]
        const criteria = {}
        criteria[field_name] = field_value
        return _.uniq(utils.filter_by.any(projects, criteria).map((item) => {
            let target = {...item}
            field_name.split('.').forEach((key)=>{
                if (target && target[key]) {
                    target = target[key]
                }
            })
            return target
        })).map((unique_value) => ({
            field: field_name,
            original: value,
            query: `${field_name}: ${unique_value}`,
            value: unique_value,
        }))
    }

    getSuggestions = (value) => {
        const suggestions = (
            this.getValueSuggestions(value)
            || this.getFieldNameSuggestions(value)
            || []
        )
        console.log(suggestions)
        return suggestions
    }

    getSuggestionValue = (suggestion) => {
        return suggestion.query;
    }

    renderSuggestion = (suggestion) => {
        return (
            <span>{suggestion.query}</span>
        );
    }
    render() {
        const { value, suggestions } = this.state;
        const inputProps = {
            placeholder: this.props.placeholder,
            defaultValue: this.props.defaultValue,
            value,
            className: `form-control col`,
            onChange: this.onChange,
            onKeyPress: this.props.onTypeQuery,
        };

        return (
            <Autosuggest
                suggestions={suggestions}
                onSuggestionsFetchRequested={this.onSuggestionsFetchRequested}
                onSuggestionsClearRequested={this.onSuggestionsClearRequested}
                getSuggestionValue={this.getSuggestionValue}
                renderSuggestion={this.renderSuggestion}
                inputProps={inputProps} />
        );
    }
}
export default QueryInput
