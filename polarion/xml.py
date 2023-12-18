import xml.etree.ElementTree as ET
from .polarion import Polarion
from .record import Record
from datetime import datetime
import logging, json
import re
logger = logging.getLogger(__name__)

class Config:
    """
    Config structure for xml importer.
    """
    XML_FILE='xml_file'                                 # Xml file to import
    URL='url'                                           # Polarion url such as http://hostname/polarion
    USERNAME='username'                                 # username to log to polarion
    PASSWORD='password'                                 # password to log to polarion
    TOKEN='token'                                       # token to log to polarion
    PROJECT_ID='project_id'                             # id of the project
    TESTRUN_ID='testrun_id'                             # id of the test run (if you want to use and existing one)
    TESTRUN_ID_GENERATOR='testrun_id_generator'         # function that generate the testrun_id (config as parameter) if testrun_id is not provided. If not set: f'unit-{datetime.now}'
    TESTRUN_TITLE='testrun_title'                       # title of the test run if testrun is created. If not set 'New unit test run'
    TESTRUN_TYPE='testrun_type'                         # type of the test run if testrun is created. If not set 'xUnit Test Manual Upload'
    TESTRUN_COMMENT='testrun_comment'                   # test run comment to add if set.
    SKIP_MISSING_TESTCASE='skip_missing_testcase'       # if set to True, skip result on unknown test cases
    VERIFY_CERT ='verify_cert'                          # verify or not the cert
    USE_CACHE ='use_cache'                              # verify or not the cert
    ATTRIBUTES = [
        XML_FILE, URL, USERNAME, PASSWORD, TOKEN, 
        PROJECT_ID, TESTRUN_ID, TESTRUN_ID_GENERATOR,
        TESTRUN_TITLE, TESTRUN_TYPE, TESTRUN_COMMENT, SKIP_MISSING_TESTCASE, VERIFY_CERT, USE_CACHE]
    MANDATORY = [XML_FILE, URL, PROJECT_ID]  # and also either user/password or token
    
    _classinitialised = False

    def __new__(cls, *args, **kwargs):
        if not Config._classinitialised:
            # Add properties dynamicaly
            for attr in Config.ATTRIBUTES:
                eval(f'setattr(Config, "{attr}", property(lambda self: self._data["{attr}"] if "{attr}" in self._data.keys() else Config._default_value("{attr}")))')
            Config._classinitialised=True
        return super().__new__(cls)
        
    @classmethod
    def _default_value(cls, attribute_name):
        if attribute_name==Config.TESTRUN_TITLE:
            return 'New unit test run'
        elif attribute_name==Config.TESTRUN_TYPE:
            return 'xUnit Test Manual Upload'
        elif attribute_name==Config.SKIP_MISSING_TESTCASE:
            return False
        elif attribute_name==Config.VERIFY_CERT:
            return True
        elif attribute_name==Config.USE_CACHE:
            return False
        return None

    @classmethod
    def from_json(cls, json):
        """
        Create config from a json file
        """
        with open(json, 'r') as f:
            return Config(json.loads(f.read()))
    
    @classmethod
    def from_dict(cls, data):
        """
        Create config from a dict
        """
        return Config(data)


    def __init__(self, data):
        """
        Init from existing data

        param data: dict to initialise.
        """
        self._data=data
        self._check_mandatory()

    def _check_mandatory(self):
        for attribute in Config.MANDATORY:
            if getattr(self, attribute) == None:
                raise Exception(attribute + ' shall be set')
        if getattr(self, Config.TOKEN)==None and (getattr(self, Config.USERNAME)==None or getattr(self, Config.PASSWORD)==None):
            raise Exception(f'Shall set either {Config.USERNAME} / {Config.PASSWORD} or {Config.TOKEN}')

    def generate_test_run_id(self):
        if getattr(self, Config.TESTRUN_ID) is None:
            if getattr(self, Config.TESTRUN_ID_GENERATOR) is not None:
                self._data[Config.TESTRUN_ID]=getattr(self, Config.TESTRUN_ID_GENERATOR)(self)
            else:
                self._data[Config.TESTRUN_ID]=f'unit-{datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")}'
        return getattr(self, Config.TESTRUN_ID)
    

class XmlParser:
    """
    Xml parser for xml_junit.xsd format
    """
    TEST_SUITES='testsuites'
    TEST_SUITE='testsuite'
    TEST_CASE='testcase'
    PROPERTIES='properties'
    PROPERTY='property'
    SYSOUT='system-out'

    @classmethod
    def parse_root(cls, xml_file):
        """
        Parse Xml file
        :return: List of cases for the file
        """
        root=ET.parse(xml_file).getroot()
        returned_cases = []
        if root.tag == XmlParser.TEST_SUITES:
            for test_suite in root:
                XmlParser._parse_suite(test_suite, { 'path': f'{xml_file}/{XmlParser.TEST_SUITES}' }, returned_cases)
        elif root.tag == XmlParser.TEST_SUITE:
            XmlParser._parse_suite(root, { 'path': f'{xml_file}/{XmlParser.TEST_SUITE}' }, returned_cases)
        else:
            raise Exception(f'Unmanaged root {root.tag} in {xml_file}')
        return returned_cases

    @classmethod
    def _parse_suite(cls, test_suite, parent, returned_cases):
        """
        Parse test_suite node child of parent and append returned_cases
        :param test_suite: test_suite node to parse
        :param parent: parent node (used for log)
        :param returned_cases: as result, append test case of the suite to this list
        """
        if test_suite.tag == XmlParser.TEST_SUITE:
            suite=parent.copy()
            suite.update({ 'path': f'{parent["path"]}/{XmlParser.TEST_SUITE}{XmlParser._xmlnode_name(test_suite)}' })
            if 'timestamp' in test_suite.attrib:
                suite.update({ 'timestamp': test_suite.attrib['timestamp'] })
            for child in test_suite:
                if child.tag == XmlParser.TEST_SUITE:
                    XmlParser._parse_suite(child, suite, returned_cases)
                if child.tag == XmlParser.TEST_CASE:
                    XmlParser._parse_case(child, suite, returned_cases)
        else:
            raise Exception(f'Unmanaged {XmlParser.TEST_SUITE} {test_suite.tag} in {parent["path"]}')

    # matches expressions like [[PROPERTY|verifies=REQ-001]]
    RE_PATTTERN = re.compile("\\[\\[PROPERTY\\|(.*)\\=(.*)\\]\\]")

    @classmethod
    def tranform_string_properties(cls, value):
        result = [] 
        tmp =  XmlParser.RE_PATTTERN.findall(value)
        for res in tmp:
            if len(res) == 2:
                result.append({
                    "name":res[0],
                    "value":res[1]
                }) 
        return result

    @classmethod
    def _parse_case(cls, test_case, parent, returned_cases):
        if test_case.tag == XmlParser.TEST_CASE:
            case=parent.copy()
            case.update({ 'path': f'{parent["path"]}/{XmlParser.TEST_CASE}{XmlParser._xmlnode_name(test_case)}' })
            # id
            if 'name' not in test_case.attrib.keys() or 'classname' not in test_case.attrib.keys():
                logger.warn(f'{case["path"]}: no name or classname. Case skipped')
                return
            case.update({ 'id': test_case.attrib['classname']+'.'+test_case.attrib['name'] })
            
            # time
            if 'time' in test_case.attrib.keys():
                case.update({ 'time': test_case.attrib['time'] })
            
            # error & failure & properties
            for elem in test_case:
                if elem.tag in ['error', 'failure','skipped']:
                    text = []
                    for attrib in ['type', 'message']:
                        if attrib in elem.attrib.keys(): text.append(elem.attrib[attrib])
                    if elem.text is not None:
                        text.append(elem.text)
                    case.update({ elem.tag: '\n'.join(text)})
                elif elem.tag == XmlParser.PROPERTIES:
                    if "properties" not in case:
                        case.update({'properties':[]})
                    for property in elem:
                        if XmlParser.PROPERTY == property.tag and 'name' in property.attrib.keys() and 'value' in property.attrib.keys():
                            case['properties'].append({property.get('name') : property.get('value')})
                elif elem.tag == XmlParser.SYSOUT:
                    if "properties" not in case:
                        case.update({'properties':[]})
                    for property in XmlParser.tranform_string_properties(elem.text):
                        case['properties'].append({property['name'] : property['value']})
            returned_cases.append(case)
        else:
            raise Exception(f'Unmanaged {XmlParser.TEST_CASE} {test_case.tag} in {parent["path"]}')

    @classmethod
    def _xmlnode_name(cls, node):
        """
        Build name of the xmlnode
        """
        if 'name' in node.attrib.keys():
            return f'{node.tag}[name={node.attrib["name"]}]'
        return node.tag
    
class Importer:
    """
    Import xml file to polarion using a config
    """
    TEST_CASE_ID_CUSTOM_FIELD='testCaseID'
    TEST_CASE_TYPE='type:testcase'
    TEST_CASE_WI_TYPE='testcase'
    TEST_CASE_WI_TITLE='title'
    TEST_RUN_COMMENT_CUSTOM_FIELD='environmentDescription'

    @classmethod
    def from_xml(cls, config):
        """
        Import xml file having junit.xsd structure (see documentation)
        """
        logger.info(f'Parsing test file {config.xml_file}')
        cases=XmlParser.parse_root(config.xml_file)

        logger.info(f'Connection to polarion {config.url} on project {config.project_id}')

        polarion=Polarion(polarion_url=config.url, user=config.username, password=config.password, token=config.token, verify_certificate=config.verify_cert, cache=config.use_cache)
        project=polarion.getProject(config.project_id)

        # Indexing existing cases with custom field '
        test_cases=project.searchWorkitem(Importer.TEST_CASE_TYPE, field_list=['id', f'customFields.{Importer.TEST_CASE_ID_CUSTOM_FIELD}'])
        test_cases_from_id={}
        for test_case in test_cases:
            if hasattr(test_case,'customFields') and hasattr(test_case.customFields,'Custom'):
                for custom in test_case.customFields.Custom:
                    if getattr(custom, 'key', None) == Importer.TEST_CASE_ID_CUSTOM_FIELD and hasattr(custom,'value'):
                        test_cases_from_id[custom.value]=test_case.id

        # Getting or creating test run
        if config.testrun_id is None:
            config.generate_test_run_id()
            logger.info(f'Creating testrun {config.testrun_id}')
            test_run=project.createTestRun(config.testrun_id, config.testrun_title, config.testrun_type)
        else:
            logger.info(f'Loading testrun {config.testrun_id}')
            test_run=project.getTestRun(config.testrun_id)

        # Updating test run
        if config.testrun_comment is not None:
            comment='<html><body>'+config.testrun_comment+'</body></html>'
            custom_field=test_run.getCustomField(Importer.TEST_RUN_COMMENT_CUSTOM_FIELD)
            if custom_field is not None:
                comment=custom_field.content
                if comment is not None:
                    split=comment.split('</body>')
                    if len(split)==2:
                        comment=split[0]+'<br>'+config.testrun_comment+'</body></html>'
                    else:
                        logger.warn(f'unable to parse properly {Importer.TEST_RUN_COMMENT_CUSTOM_FIELD} of testrun: {comment}. So it is not updated')
            test_run.setCustomField(Importer.TEST_RUN_COMMENT_CUSTOM_FIELD, test_run._polarion.TextType(
                    content=comment, type='text/html', contentLossy=False))

        # cache for work items traced
        cache_for_workitems = {}

        # Filling
        logger.info('Saving results')
        for case in cases:
            if case['id'] not in test_cases_from_id.keys():
                if config.skip_missing_testcase:
                    logger.warn(f'Skipping case with {Importer.TEST_CASE_ID_CUSTOM_FIELD} {case["id"]}')
                    continue
                print(f'Creating case with {Importer.TEST_CASE_ID_CUSTOM_FIELD} {case["id"]}')
                wi_case=project.createWorkitem(workitem_type=Importer.TEST_CASE_WI_TYPE, new_workitem_fields={Importer.TEST_CASE_WI_TITLE: case['id']})
                wi_case.setCustomField(key=Importer.TEST_CASE_ID_CUSTOM_FIELD, value=case['id'])
            else:
                wi_case=project.getWorkitem(test_cases_from_id[case['id']])
            test_run.addTestcase(wi_case)
            
            if 'time' in case.keys():
                test_run.records[-1].duration=case['time']

            if 'timestamp' in case.keys():
                test_run.records[-1].executed=case['timestamp']

            if 'failure' in case.keys():
                test_run.records[-1].setResult(Record.ResultType.FAILED, case['failure'])
            elif 'error' in case.keys():
                test_run.records[-1].setResult(Record.ResultType.BLOCKED, case['error'])
            elif 'skipped' in case.keys():
                test_run.records[-1].setResult(Record.ResultType.NOTTESTED, case['skipped'])
            else:
                test_run.records[-1].setResult(Record.ResultType.PASSED)
            
            # handle traceability, because of API, traqceability must use default traceability role 
            # and not the opposite one.
            # traceability links are made using IDs or titles 
            # this implementation does not allow traceability between test cases
            if 'properties' in case.keys():
                for property in case['properties']:
                    for key in property.keys():
                        linked_item = None
                        title=property.get(key)
                        if title in cache_for_workitems:
                            linked_item = cache_for_workitems[title]
                        else:
                            try:
                                linked_item=project.getWorkitem(property.get(key))
                            except Exception:
                                linked_items=project.searchWorkitem(query=f'title:{title}', field_list=['id','title'])
                                if len(linked_items) > 0 and linked_items[0]['title']==title:
                                    linked_item=linked_items[0]
                                    # work item is reload to avoid isues of class not correctly loaded by search work item
                                    linked_item=project.getWorkitem(linked_item['id'])
                                else:
                                    logger.error(f'impossible to link{wi_case.id} to {title}')
                                cache_for_workitems[title] = linked_item
                        if linked_item is not None:
                            wi_case.addLinkedItem(linked_item, key)

        logger.info(f'Results saved in {config.url}/#/project/{config.project_id}/testrun?id={config.testrun_id}')

        return test_run

class ResultExporter:
    """
    Export an object as a json (tested with a testrun)
    """
    @classmethod
    def _make_serialisable(cls, obj):
        if isinstance(obj, str):
            return obj
        elif isinstance(obj, int):
            return str(obj)
        elif isinstance(obj, float):
            return str(obj)
        elif isinstance(obj, bool):
            return obj
        elif isinstance(obj, list):
            return [ResultExporter._make_serialisable(item) for item in obj]
        elif isinstance(obj, dict):
            for key,val in obj.items():
                obj[key]=ResultExporter._make_serialisable(val)
            return obj
        elif isinstance(obj, datetime):
            return obj.strftime('%d-%m-%Y-%H-%M-%S-%f')
        elif str(type(obj))=="<class 'zeep.objects.ArrayOfTestRecord'>":
            return ResultExporter._make_serialisable(obj.TestRecord)
        elif str(type(obj))=="<class 'zeep.objects.ArrayOfCustom'>":
            return ResultExporter._make_serialisable(obj.Custom)
        elif str(type(obj))=="<class 'zeep.objects.ArrayOfEnumOptionId'>":
            return ResultExporter._make_serialisable(obj.EnumOptionId)
        elif str(type(obj))=="<class 'zeep.objects.EnumOptionId'>":
            return obj.id
        elif str(type(obj))=="<class 'zeep.objects.Custom'>":
            return { 'key': obj.key, 'value': ResultExporter._make_serialisable(obj.value) }
        elif str(type(obj))=="<class 'zeep.objects.Text'>":
            return obj.content
        elif str(type(obj))=="<class 'polarion.testrun.Testrun'>":
            return ResultExporter._make_serialisable(dict(obj._polarion_test_run.__dict__['__values__']).copy())
        elif str(type(obj))=="<class 'zeep.objects.TestRecord'>":
            return ResultExporter._make_serialisable(dict(obj.__dict__['__values__']).copy())
        elif type(obj)==type(None):
            return None
        else:
            print('[WARN] Not processed type: '+str(type(obj))+' having value: '+str(obj))
            return str(obj)

    @classmethod
    def save_json(cls, results_file, test_run):
        logger.info(f'Saving results in {results_file}')
        result=ResultExporter._make_serialisable(test_run)
        with open(results_file, 'w') as outfile:
            outfile.write(json.dumps(result, indent=4))
