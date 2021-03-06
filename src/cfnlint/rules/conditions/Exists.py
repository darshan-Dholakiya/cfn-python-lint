"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Exists(CloudFormationLintRule):
    """Check if used Conditions are defined """
    id = 'E8002'
    shortdesc = 'Check if the referenced Conditions are defined'
    description = 'Making sure the used conditions are actually defined in the Conditions section'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html'
    tags = ['conditions']

    def match(self, cfn):
        """Check CloudFormation Conditions"""

        matches = []
        ref_conditions = {}

        # Get all defined conditions
        conditions = cfn.template.get('Conditions', {})

        # Get all "If's" that reference a Condition
        iftrees = cfn.search_deep_keys('Fn::If')
        for iftree in iftrees:
            if isinstance(iftree[-1], list):
                ref_conditions[iftree[-1][0]] = iftree
            else:
                ref_conditions[iftree[-1]] = iftree

        # Get resource's Conditions
        for resource_name, resource_values in cfn.get_resources().items():
            if 'Condition' in resource_values:
                path = ['Resources', resource_name, 'Condition']
                ref_conditions[resource_values['Condition']] = path

        # Get conditions used by another condition
        condtrees = cfn.search_deep_keys('Condition')

        for condtree in condtrees:
            if condtree[0] == 'Conditions':
                if isinstance(condtree[-1], (str, six.text_type, six.string_types)):
                    path = ['Conditions', condtree[-1]]
                    ref_conditions[condtree[-1]] = path

        # Get Output Conditions
        for _, output_values in cfn.template.get('Outputs', {}).items():
            if 'Condition' in output_values:
                path = ['Outputs', output_values['Condition']]
                ref_conditions[output_values['Condition']] = path

        # Check if all the conditions are defined
        for ref_condition, ref_path in ref_conditions.items():
            if ref_condition not in conditions:
                message = 'Condition {0} is not defined.'
                matches.append(RuleMatch(
                    ref_path,
                    message.format(ref_condition)
                ))

        return matches
