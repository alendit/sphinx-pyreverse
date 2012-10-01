# -*- coding: utf-8 -*-
from types import MethodType, FunctionType
from copy import copy
from xml.dom import minidom, Node
import urllib, urllib2
from urllib2 import HTTPError
from synchroassistent import settings
from django.db import models

class WebService(object):
    """Represents a webservice with a factory class to wrap the resopnse into"""
    def __init__(self, name, factory_class, params=(), description="", default_params={},
                 call_name=""):
        self.name = name
        assert isinstance(params, tuple), "params has to be a tuple"
        self.params = params
        self.factory_class = factory_class
        self.decription = description
        self.default_params = default_params
        self.call_name = call_name
        
class CurrentWebService(WebService):
    """WebService which always sends a current year and semester as parameters"""
    
    CURRENT_PARAMETERS = {"st_year" : settings.CURRENT_ST_YEAR,
                          "st_semester" : settings.CURRENT_SEMESTER,
                          }
    def __init__(self, name, factory_class, params=(), description="", default_params={},
                 call_name=""):
        default_params.update(self.CURRENT_PARAMETERS)
        super(CurrentWebService, self).__init__(
                name, factory_class, params, description, default_params, call_name)

class Course(object):
    """Represents a single course"""
    
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.checked = None
        self.group_manager = GroupCoursesManager(id)
        
    def __cmp__(self, other):
        return cmp((self.checked, self.title),
                   (other.checked, other.title))

class Student(object):
    """Represents a student entity in TUMOnline and moodle"""
    
    def __init__(self, id, fname, lname, email):
        self.id = id
        self.fname = fname
        self.lname = lname
        self.email = email
        self.checked = None
        
    def __cmp__(self, other):
        return cmp((self.checked, self.lname, self.fname),
                   (other.checked, other.lname, other.fname))
        
class Group(object):
    """Represents a single groups"""
    
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.checked = None
        
    def __cmp__(self, other):
        return cmp((self.checked, self.title),
           (other.checked, other.title))

class AddProxyMetaclass(type):
    def __new__(cls, name, bases, attr_dict):
        def create_caller(service):
            def ws_caller(self, *args, **kwargs):
                ws_params = {}
                ws_params.update(service.default_params)
                ws_params.update(dict(zip(service.params, args)))
                assert set(kwargs.keys()).issubset(service.params)
                ws_params.update(kwargs)
                ws_name = service.call_name or service.name
                return self.call_webservice_by_name(
                    ws_name, service.factory_class, ws_params)
            ws_caller.__doc__ = "{0}.\nParameters: {1}.\nDefault parameters: {2}"\
                    .format(service.decription, service.params, service.default_params)
            return ws_caller

        for service in attr_dict['registered_webservices']:
            attr_dict[service.name] = create_caller(service)
        return type.__new__(cls, name, bases, attr_dict)

class WSProxy(object):
    """Wraps webservice calls, returning objects"""
    
    registered_webservices = []
    __metaclass__ = AddProxyMetaclass
    
    def call_webservice(self, webservice_url, factory_class, ws_parameter={}):
        """Calls a webservice and returns a list of objects with attributes"""
        ws_parameter.update({"token" : self.TOKEN})
        url_parameter = "?%s" % urllib.urlencode(ws_parameter) if ws_parameter else ""
        ws_call_url = "%s%s" % (webservice_url, url_parameter)
	print ws_call_url
        try:
            opener = urllib2.urlopen(ws_call_url)
        except HTTPError, e:
            return []
        return self.ws_xml_to_object(opener, factory_class)
    
    
    def call_webservice_by_name(self, webservice, factory_class, ws_parameter={}):
        """Calls webservice with the parameters for current semester"""
        web_service = self.registered_webservices
        return self.call_webservice\
                (self.WEBPACKAGE_URL + webservice, factory_class, ws_parameter)
    
    def ws_xml_to_object(self, stream, factory_class):
        """Takes an xml stream and returns a list of objects with attributes"""
	try:
            ws_dom = minidom.parse(stream)
	except:
   	    return []
        objects = []
        for obj in ws_dom.childNodes[0].childNodes:
            if self.is_object_node(obj):
                attrs = {}
                for attr in obj.childNodes:
                    if self.is_object_node(attr):
                        attrs[attr.nodeName] = attr.childNodes[0].nodeValue
                objects.append(factory_class(**attrs))
        return objects
    
    def is_object_node(self, node):
        """Checks if the node is not an empty node generated by a \n"""
        return not (node.nodeType == Node.TEXT_NODE and\
             node.nodeValue.replace("\n", "").replace(" ", "") == "")
        

class TUMOnlineProxy(WSProxy):
    """Wraps the webservice calls to tumonline"""
    
    WEBPACKAGE_URL = settings.TUMONLINE_WEBPACKAGE_URL
    TOKEN = settings.TUMONLINE_TOKEN
    registered_webservices = [
        CurrentWebService("get_all_courses",  Course,
            description="""Returns all elearning objects in the current term"""),
        WebService("get_courses_by_id",  Course,  ("id",),
            description="""Returns a list with a single course object by id"""),
        CurrentWebService("get_courses_by_student_id",  Course, ("id",),
            description="""Returns a list of objects for the student in the current term"""),
        WebService("get_courses_by_name",  Course, ("course_name",),
            description="""Returns a list of objects matching a given criteria (title)"""),
        WebService("get_students_by_id",  Student, ("id",),
            description="""Return a list with a single user by his lrz id"""),
        WebService("get_students_by_course_id",  Student, ("id",),
            description="""Returns a list of objects in the given course"""),
        WebService("get_students_by_name",  Student, ("fname", "lname"),
            description="""Returns a list of objects matching search criteria (name, given name)"""),
        WebService("get_students_by_lastname",  Student, ("lname",),
            description="""Returns a list of objects matching search criteria (name)"""),
        WebService("get_groups_by_course_id", Group, ("id",),
                   description="""Returns a list of group for a given course""")
        ]
                
    
    def get_student_xml_by_id(self, course_id, student_id):
        """Retuns a xml element corresponding to a give student id"""
        webservice_url = "%sget_student_xml_by_id" % self.WEBPACKAGE_URL
        url_parameter = urllib.urlencode({"course_id" : course_id,
                                          "student_id" : student_id,
                                          "token" : self.TOKEN,
                                          })
        ws_call_url = "%s?%s" % (webservice_url, url_parameter)
        opener = urllib2.urlopen(ws_call_url)
        ws_dom = minidom.parse(opener)
        return ws_dom.childNodes[0].childNodes[1]

        
    
class MoodleProxy(WSProxy):
    """Wraps the webservice calls to moodle"""
    WEBPACKAGE_URL = settings.MOODLE_WEBPACKAGE_URL
    TOKEN = settings.MOODLE_TOKEN
    
    def ws_xml_to_object(self, stream, class_factory):
        """Converts student-elements to student objects"""
        ws_dom = minidom.parse(stream)
        work_elements = ws_dom.getElementsByTagName("students")\
                            or ws_dom.getElementsByTagName("lectures")
        objects = []
        for student in work_elements[0].childNodes:
            if self.is_object_node(student):
                args = [attr.childNodes[0].nodeValue for attr in student.childNodes
                        if self.is_object_node(attr)]
                objects.append(class_factory(*args))
        return objects
    
    registered_webservices = [
                              
            WebService("get_students_by_course_id", Student, ("cid",),
            call_name='course_tn_xml_export.php'),
            #WebService("get_courses_by_student", Course, ("id",)),
            ]
    
class ObjectManager(object):
    
    def __len__(self):
        return len(self.objects)
    
    def sort(self):
        self.objects = sorted(self.objects)

class RelatedManager(ObjectManager):
    """Parent class for object manager which create a list of related object
    and check synchronization between tumonline and moodle"""
    
    def __init__(self, objects, related_id):
        self.objects = objects
        self.related_id = related_id
        self.check_synchro()
        
    def __getitem__(self, index):
        return self.objects[index]
    
    def get_moodle_related_id_list(self):
        """Returns a list of related ids to check against objects. Must be implemented
        in child classes"""
        pass
    
    def check_synchro(self):
        """Check synchronissation of the objects with moodle"""
        related_id_list = self.get_moodle_related_id_list()
        for obj in self.objects:
            obj.checked = obj.id in related_id_list
        
class DirectCoursesManager(ObjectManager):
    """Wraper for directly access objects by id of title. Empty selector returns
    all eLearning objects"""
    
    def __getitem__(self, index):
        return self.objects[index]
    
    def __init__(self, selector):
        self.objects = []
        if selector:
            self.objects = tumonline_proxy.get_courses_by_id(selector)
            if not self.objects:
                self.objects = tumonline_proxy.get_courses_by_name(selector)
        else:
            self.objects = tumonline_proxy.get_all_courses()
    
class StudentCoursesManager(RelatedManager):
    """Wraper for accessing objects related to a student"""
    
    def __init__(self, student_id):
        objects = tumonline_proxy.get_courses_by_student_id(student_id)
        super(StudentCoursesManager, self).__init__(objects=objects,
                                                     related_id=student_id)
    
    # reserved for when get_courses_by_student gets implemented
    #def check_syncro(self):
    #    """Check the objects against the objects list from moodle"""
    #    moodle_courses = dict([(course.id, course) for course in \
    #                        moodle_proxy.get_courses_by_student(self.student_id)])
    #    for tum_course in self.objects:
    #        tum_course.checked = tum_course.id in moodle_courses
    
    def check_synchro(self):
        for tum_course in self.objects:
            student_id_list = (student.id for student in
                moodle_proxy.get_students_by_course_id(tum_course.id))
            tum_course.checked = self.related_id in student_id_list


class DirectStudentsManager(ObjectManager):
    
    def __getitem__(self, index):
        return self.objects[index]
    
    """Wraper to access a set of student directly over a selector (id or name)"""
    def __init__(self, selector):
        self.objects = tumonline_proxy.get_students_by_id(selector)
        if not self.objects:
            # create first and second name arguments by spliting at space
            names = selector.split(" ")
            names = [name.capitalize() for name in names]
            if len(names) == 1:
                self.objects = tumonline_proxy.get_students_by_lastname(names[0])
            else:
                # If the first name has more than 1 word use only the first one
                fname, lname = names[0], names[-1]
                self.objects = tumonline_proxy.get_students_by_name(fname, lname)
                lname, fname = names[0], names[1]
                self.objects += tumonline_proxy.get_students_by_name(fname, lname)
                if not self.objects:
                    lname = fname
                    self.objects = tumonline_proxy.get_students_by_lastname(names[-1])
                    self.objects += tumonline_proxy.get_students_by_lastname(names[0])
    
            
class CourseStudentsManager(RelatedManager):
    """Wraper to access a set of objects by id of the related course"""
    def __init__(self, course_id):
        students = tumonline_proxy.get_students_by_course_id(course_id)
        super(CourseStudentsManager, self).__init__(objects=students,
                                                    related_id=course_id)
        
    def get_moodle_related_id_list(self):
        return [student.id for student in 
                moodle_proxy.get_students_by_course_id(self.related_id)]
        
class GroupCoursesManager(RelatedManager):
    """Wrapper to access a set of groups by id of the lated course"""
    def __init__(self, course_id):
        groups = tumonline_proxy.get_groups_by_course_id(course_id)
        super(GroupCoursesManager, self).__init__(objects=groups,
                                                  related_id=course_id)
        
    def get_moodle_related_id_list(self):
        """TODO: Implement"""
        return []
    
tumonline_proxy = TUMOnlineProxy()
moodle_proxy = MoodleProxy()
