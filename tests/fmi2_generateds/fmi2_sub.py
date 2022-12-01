#!/usr/bin/env python

#
# Generated  by generateDS.py.
# Python 3.10.2 (tags/v3.10.2:a58ebcc, Jan 17 2022, 14:12:15) [MSC v.1929 64 bit (AMD64)]
#
# Command line options:
#   ('-f', '')
#   ('-o', 'fmi2_api.py')
#   ('-s', 'fmi2_sub.py')
#   ('--no-dates', '')
#   ('--no-versions', '')
#   ('--no-redefine-groups', '')
#   ('--disable-generatedssuper-lookup', '')
#   ('--disable-xml', '')
#   ('--create-mandatory-children', '')
#
# Command line arguments:
#   fmi2ModelDescription.xsd
#
# Command line:
#   C:\Dev\ospx\.venv\Scripts\generateDS -f -o "fmi2_api.py" -s "fmi2_sub.py" --no-dates --no-versions --no-redefine-groups --disable-generatedssuper-lookup --disable-xml --create-mandatory-children fmi2ModelDescription.xsd
#
# Current working directory (os.getcwd()):
#   fmi2_generateds
#

import os
import sys
## from lxml import etree as etree_

import ??? as supermod

## def parsexml_(infile, parser=None, **kwargs):
##     if parser is None:
##         # Use the lxml ElementTree compatible parser so that, e.g.,
##         #   we ignore comments.
##         parser = etree_.ETCompatXMLParser()
##     try:
##         if isinstance(infile, os.PathLike):
##             infile = os.path.join(infile)
##     except AttributeError:
##         pass
##     doc = etree_.parse(infile, parser=parser, **kwargs)
##     return doc

## def parsexmlstring_(instring, parser=None, **kwargs):
##     if parser is None:
##         # Use the lxml ElementTree compatible parser so that, e.g.,
##         #   we ignore comments.
##         try:
##             parser = etree_.ETCompatXMLParser()
##         except AttributeError:
##             # fallback to xml.etree
##             parser = etree_.XMLParser()
##     element = etree_.fromstring(instring, parser=parser, **kwargs)
##     return element

#
# Globals
#

ExternalEncoding = ''
SaveElementTreeNode = True

#
# Data representation classes
#


class fmiModelDescriptionSub(supermod.fmiModelDescription):
    def __init__(self, fmiVersion='2.0', modelName=None, guid=None, description=None, author=None, version=None, copyright=None, license=None, generationTool=None, generationDateAndTime=None, variableNamingConvention='flat', numberOfEventIndicators=None, ModelExchange=None, CoSimulation=None, UnitDefinitions=None, TypeDefinitions=None, LogCategories=None, DefaultExperiment=None, VendorAnnotations=None, ModelVariables=None, ModelStructure=None, **kwargs_):
        super(fmiModelDescriptionSub, self).__init__(fmiVersion, modelName, guid, description, author, version, copyright, license, generationTool, generationDateAndTime, variableNamingConvention, numberOfEventIndicators, ModelExchange, CoSimulation, UnitDefinitions, TypeDefinitions, LogCategories, DefaultExperiment, VendorAnnotations, ModelVariables, ModelStructure,  **kwargs_)
supermod.fmiModelDescription.subclass = fmiModelDescriptionSub
# end class fmiModelDescriptionSub


class fmi2ScalarVariableSub(supermod.fmi2ScalarVariable):
    def __init__(self, name=None, valueReference=None, description=None, causality='local', variability='continuous', initial=None, canHandleMultipleSetPerTimeInstant=None, Real=None, Integer=None, Boolean=None, String=None, Enumeration=None, Annotations=None, **kwargs_):
        super(fmi2ScalarVariableSub, self).__init__(name, valueReference, description, causality, variability, initial, canHandleMultipleSetPerTimeInstant, Real, Integer, Boolean, String, Enumeration, Annotations,  **kwargs_)
supermod.fmi2ScalarVariable.subclass = fmi2ScalarVariableSub
# end class fmi2ScalarVariableSub


class fmi2AnnotationSub(supermod.fmi2Annotation):
    def __init__(self, Tool=None, **kwargs_):
        super(fmi2AnnotationSub, self).__init__(Tool,  **kwargs_)
supermod.fmi2Annotation.subclass = fmi2AnnotationSub
# end class fmi2AnnotationSub


class fmi2VariableDependencySub(supermod.fmi2VariableDependency):
    def __init__(self, Unknown=None, **kwargs_):
        super(fmi2VariableDependencySub, self).__init__(Unknown,  **kwargs_)
supermod.fmi2VariableDependency.subclass = fmi2VariableDependencySub
# end class fmi2VariableDependencySub


class fmi2UnitSub(supermod.fmi2Unit):
    def __init__(self, name=None, BaseUnit=None, DisplayUnit=None, **kwargs_):
        super(fmi2UnitSub, self).__init__(name, BaseUnit, DisplayUnit,  **kwargs_)
supermod.fmi2Unit.subclass = fmi2UnitSub
# end class fmi2UnitSub


class fmi2SimpleTypeSub(supermod.fmi2SimpleType):
    def __init__(self, name=None, description=None, Real=None, Integer=None, Boolean=None, String=None, Enumeration=None, **kwargs_):
        super(fmi2SimpleTypeSub, self).__init__(name, description, Real, Integer, Boolean, String, Enumeration,  **kwargs_)
supermod.fmi2SimpleType.subclass = fmi2SimpleTypeSub
# end class fmi2SimpleTypeSub


class ModelExchangeTypeSub(supermod.ModelExchangeType):
    def __init__(self, modelIdentifier=None, needsExecutionTool=False, completedIntegratorStepNotNeeded=False, canBeInstantiatedOnlyOncePerProcess=False, canNotUseMemoryManagementFunctions=False, canGetAndSetFMUstate=False, canSerializeFMUstate=False, providesDirectionalDerivative=False, SourceFiles=None, **kwargs_):
        super(ModelExchangeTypeSub, self).__init__(modelIdentifier, needsExecutionTool, completedIntegratorStepNotNeeded, canBeInstantiatedOnlyOncePerProcess, canNotUseMemoryManagementFunctions, canGetAndSetFMUstate, canSerializeFMUstate, providesDirectionalDerivative, SourceFiles,  **kwargs_)
supermod.ModelExchangeType.subclass = ModelExchangeTypeSub
# end class ModelExchangeTypeSub


class SourceFilesTypeSub(supermod.SourceFilesType):
    def __init__(self, File=None, **kwargs_):
        super(SourceFilesTypeSub, self).__init__(File,  **kwargs_)
supermod.SourceFilesType.subclass = SourceFilesTypeSub
# end class SourceFilesTypeSub


class FileTypeSub(supermod.FileType):
    def __init__(self, name=None, **kwargs_):
        super(FileTypeSub, self).__init__(name,  **kwargs_)
supermod.FileType.subclass = FileTypeSub
# end class FileTypeSub


class CoSimulationTypeSub(supermod.CoSimulationType):
    def __init__(self, modelIdentifier=None, needsExecutionTool=False, canHandleVariableCommunicationStepSize=False, canInterpolateInputs=False, maxOutputDerivativeOrder=0, canRunAsynchronuously=False, canBeInstantiatedOnlyOncePerProcess=False, canNotUseMemoryManagementFunctions=False, canGetAndSetFMUstate=False, canSerializeFMUstate=False, providesDirectionalDerivative=False, SourceFiles=None, **kwargs_):
        super(CoSimulationTypeSub, self).__init__(modelIdentifier, needsExecutionTool, canHandleVariableCommunicationStepSize, canInterpolateInputs, maxOutputDerivativeOrder, canRunAsynchronuously, canBeInstantiatedOnlyOncePerProcess, canNotUseMemoryManagementFunctions, canGetAndSetFMUstate, canSerializeFMUstate, providesDirectionalDerivative, SourceFiles,  **kwargs_)
supermod.CoSimulationType.subclass = CoSimulationTypeSub
# end class CoSimulationTypeSub


class SourceFilesType1Sub(supermod.SourceFilesType1):
    def __init__(self, File=None, **kwargs_):
        super(SourceFilesType1Sub, self).__init__(File,  **kwargs_)
supermod.SourceFilesType1.subclass = SourceFilesType1Sub
# end class SourceFilesType1Sub


class FileType2Sub(supermod.FileType2):
    def __init__(self, name=None, **kwargs_):
        super(FileType2Sub, self).__init__(name,  **kwargs_)
supermod.FileType2.subclass = FileType2Sub
# end class FileType2Sub


class UnitDefinitionsTypeSub(supermod.UnitDefinitionsType):
    def __init__(self, Unit=None, **kwargs_):
        super(UnitDefinitionsTypeSub, self).__init__(Unit,  **kwargs_)
supermod.UnitDefinitionsType.subclass = UnitDefinitionsTypeSub
# end class UnitDefinitionsTypeSub


class TypeDefinitionsTypeSub(supermod.TypeDefinitionsType):
    def __init__(self, SimpleType=None, **kwargs_):
        super(TypeDefinitionsTypeSub, self).__init__(SimpleType,  **kwargs_)
supermod.TypeDefinitionsType.subclass = TypeDefinitionsTypeSub
# end class TypeDefinitionsTypeSub


class LogCategoriesTypeSub(supermod.LogCategoriesType):
    def __init__(self, Category=None, **kwargs_):
        super(LogCategoriesTypeSub, self).__init__(Category,  **kwargs_)
supermod.LogCategoriesType.subclass = LogCategoriesTypeSub
# end class LogCategoriesTypeSub


class CategoryTypeSub(supermod.CategoryType):
    def __init__(self, name=None, description=None, **kwargs_):
        super(CategoryTypeSub, self).__init__(name, description,  **kwargs_)
supermod.CategoryType.subclass = CategoryTypeSub
# end class CategoryTypeSub


class DefaultExperimentTypeSub(supermod.DefaultExperimentType):
    def __init__(self, startTime=None, stopTime=None, tolerance=None, stepSize=None, **kwargs_):
        super(DefaultExperimentTypeSub, self).__init__(startTime, stopTime, tolerance, stepSize,  **kwargs_)
supermod.DefaultExperimentType.subclass = DefaultExperimentTypeSub
# end class DefaultExperimentTypeSub


class ModelVariablesTypeSub(supermod.ModelVariablesType):
    def __init__(self, ScalarVariable=None, **kwargs_):
        super(ModelVariablesTypeSub, self).__init__(ScalarVariable,  **kwargs_)
supermod.ModelVariablesType.subclass = ModelVariablesTypeSub
# end class ModelVariablesTypeSub


class ModelStructureTypeSub(supermod.ModelStructureType):
    def __init__(self, Outputs=None, Derivatives=None, InitialUnknowns=None, **kwargs_):
        super(ModelStructureTypeSub, self).__init__(Outputs, Derivatives, InitialUnknowns,  **kwargs_)
supermod.ModelStructureType.subclass = ModelStructureTypeSub
# end class ModelStructureTypeSub


class InitialUnknownsTypeSub(supermod.InitialUnknownsType):
    def __init__(self, Unknown=None, **kwargs_):
        super(InitialUnknownsTypeSub, self).__init__(Unknown,  **kwargs_)
supermod.InitialUnknownsType.subclass = InitialUnknownsTypeSub
# end class InitialUnknownsTypeSub


class UnknownTypeSub(supermod.UnknownType):
    def __init__(self, index=None, dependencies=None, dependenciesKind=None, **kwargs_):
        super(UnknownTypeSub, self).__init__(index, dependencies, dependenciesKind,  **kwargs_)
supermod.UnknownType.subclass = UnknownTypeSub
# end class UnknownTypeSub


class RealTypeSub(supermod.RealType):
    def __init__(self, declaredType=None, start=None, derivative=None, reinit=False, quantity=None, unit=None, displayUnit=None, relativeQuantity=False, min=None, max=None, nominal=None, unbounded=False, **kwargs_):
        super(RealTypeSub, self).__init__(declaredType, start, derivative, reinit, quantity, unit, displayUnit, relativeQuantity, min, max, nominal, unbounded,  **kwargs_)
supermod.RealType.subclass = RealTypeSub
# end class RealTypeSub


class IntegerTypeSub(supermod.IntegerType):
    def __init__(self, declaredType=None, start=None, quantity=None, min=None, max=None, **kwargs_):
        super(IntegerTypeSub, self).__init__(declaredType, start, quantity, min, max,  **kwargs_)
supermod.IntegerType.subclass = IntegerTypeSub
# end class IntegerTypeSub


class BooleanTypeSub(supermod.BooleanType):
    def __init__(self, declaredType=None, start=None, **kwargs_):
        super(BooleanTypeSub, self).__init__(declaredType, start,  **kwargs_)
supermod.BooleanType.subclass = BooleanTypeSub
# end class BooleanTypeSub


class StringTypeSub(supermod.StringType):
    def __init__(self, declaredType=None, start=None, **kwargs_):
        super(StringTypeSub, self).__init__(declaredType, start,  **kwargs_)
supermod.StringType.subclass = StringTypeSub
# end class StringTypeSub


class EnumerationTypeSub(supermod.EnumerationType):
    def __init__(self, declaredType=None, quantity=None, min=None, max=None, start=None, **kwargs_):
        super(EnumerationTypeSub, self).__init__(declaredType, quantity, min, max, start,  **kwargs_)
supermod.EnumerationType.subclass = EnumerationTypeSub
# end class EnumerationTypeSub


class ToolTypeSub(supermod.ToolType):
    def __init__(self, name=None, anytypeobjs_=None, **kwargs_):
        super(ToolTypeSub, self).__init__(name, anytypeobjs_,  **kwargs_)
supermod.ToolType.subclass = ToolTypeSub
# end class ToolTypeSub


class UnknownType3Sub(supermod.UnknownType3):
    def __init__(self, index=None, dependencies=None, dependenciesKind=None, **kwargs_):
        super(UnknownType3Sub, self).__init__(index, dependencies, dependenciesKind,  **kwargs_)
supermod.UnknownType3.subclass = UnknownType3Sub
# end class UnknownType3Sub


class BaseUnitTypeSub(supermod.BaseUnitType):
    def __init__(self, kg=0, m=0, s=0, A=0, K=0, mol=0, cd=0, rad=0, factor=1, offset=0, **kwargs_):
        super(BaseUnitTypeSub, self).__init__(kg, m, s, A, K, mol, cd, rad, factor, offset,  **kwargs_)
supermod.BaseUnitType.subclass = BaseUnitTypeSub
# end class BaseUnitTypeSub


class DisplayUnitTypeSub(supermod.DisplayUnitType):
    def __init__(self, name=None, factor=1, offset=0, **kwargs_):
        super(DisplayUnitTypeSub, self).__init__(name, factor, offset,  **kwargs_)
supermod.DisplayUnitType.subclass = DisplayUnitTypeSub
# end class DisplayUnitTypeSub


class RealType6Sub(supermod.RealType6):
    def __init__(self, quantity=None, unit=None, displayUnit=None, relativeQuantity=False, min=None, max=None, nominal=None, unbounded=False, **kwargs_):
        super(RealType6Sub, self).__init__(quantity, unit, displayUnit, relativeQuantity, min, max, nominal, unbounded,  **kwargs_)
supermod.RealType6.subclass = RealType6Sub
# end class RealType6Sub


class IntegerType7Sub(supermod.IntegerType7):
    def __init__(self, quantity=None, min=None, max=None, **kwargs_):
        super(IntegerType7Sub, self).__init__(quantity, min, max,  **kwargs_)
supermod.IntegerType7.subclass = IntegerType7Sub
# end class IntegerType7Sub


class EnumerationType8Sub(supermod.EnumerationType8):
    def __init__(self, quantity=None, Item=None, **kwargs_):
        super(EnumerationType8Sub, self).__init__(quantity, Item,  **kwargs_)
supermod.EnumerationType8.subclass = EnumerationType8Sub
# end class EnumerationType8Sub


class ItemTypeSub(supermod.ItemType):
    def __init__(self, name=None, value=None, description=None, **kwargs_):
        super(ItemTypeSub, self).__init__(name, value, description,  **kwargs_)
supermod.ItemType.subclass = ItemTypeSub
# end class ItemTypeSub


