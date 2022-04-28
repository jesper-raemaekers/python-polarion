import unittest
from unittest.mock import patch
from polarion.utils import *


class TestPolarionUtils(unittest.TestCase):

    def test_clean_html(self):
        core_text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu libero ipsum. Nullam eget augue'
        html_text = f'<p><img src="bla"/>{core_text}</p></br>'

        clean_text = strip_html(html_text)

        self.assertEqual(core_text, clean_text, msg="Cleaned text was not equal to expected core text")

    def test_html_formatter(self):
        html_text = """big text<br/>
                        normal text<br/>
                        <span data-source="a=b" data-inline="false" class="polarion-rte-formula"></span>
                        <table id="polarion_wiki macro name=table" class="polarion-Document-table" style="width: 80%;margin-left: auto;margin-right: auto;border: 1px solid #CCCCCC;empty-cells: show;border-collapse: collapse;">
                          <tbody>
                            <tr>
                              <th style="font-weight: bold;background-color: #F0F0F0;text-align: left;vertical-align: top;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">1</th>
                              <th style="font-weight: bold;background-color: #F0F0F0;text-align: left;vertical-align: top;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">2</th>
                            </tr>
                            <tr>
                              <td style="text-align: left;vertical-align: top;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">3</td>
                              <td style="text-align: left;vertical-align: top;height: 12px;border: 1px solid #CCCCCC;padding: 5px;">4</td>
                            </tr>
                          </tbody>
                        </table>
                        <br/>"""

        expected_output =  ('big text\n'
                            'normal text\n'
                            'a=b\n'
                            '+---+---+\n'
                            '| 1 | 2 |\n'
                            '+===+===+\n'
                            '| 3 | 4 |\n'
                            '+---+---+\n')


        parser = DescriptionParser()

        parser.feed(html_text)
        actual_output = parser.data.replace(" ", "")  # remove spaces for easier comparison
        expected_output = expected_output.replace(" ", "")  # remove spaces for easier comparison

        self.assertEqual(expected_output, actual_output, msg='Parser result deviated from expected.')

    @patch('polarion.project.Project')
    def test_links(self, project_mock):
        html_text = '<span class="polarion-rte-link" data-type="workItem" id="fake" data-item-id="PYTH-510" data-option-id="long"></span>' \
                    '<span class="polarion-rte-link" data-type="workItem" id="fake" data-item-id="PYTH-510" data-option-id="short"></span>' \
                    '</span> <br/>'

        workitem_pyth_510_title = 'title of 510'
        expected_text = f'{workitem_pyth_510_title}PYTH-510'
        project_mock.getWorkitem.return_value = workitem_pyth_510_title

        # test with a project mock supplied.\
        # it should replace the 'long' tag with the title
        parser = DescriptionParser(project_mock)
        parser.feed(html_text)

        self.assertEqual(expected_text.strip(), parser.data.strip(),
                         msg='Parser workitem text did not match using project to find title')

        # with no project supplied it should default back to short
        expected_text = f'PYTH-510PYTH-510'

        parser = DescriptionParser()
        parser.feed(html_text)

        self.assertEqual(expected_text.strip(), parser.data.strip(), msg='Parser workitem text did not match')

