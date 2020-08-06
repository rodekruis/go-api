from datetime import datetime
from enumfields import EnumIntegerField
from enumfields import IntEnum

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils.hashable import make_hashable
from django.utils.encoding import force_str
from django.contrib.postgres.fields import ArrayField

from api.models import District, Country, Region, Event, DisasterType, Appeal, VisibilityCharChoices

DATE_FORMAT = '%Y/%m/%d %H:%M'


class ERUType(IntEnum):
    BASECAMP = 0
    TELECOM = 1
    LOGISTICS = 2
    EMERGENCY_HOSPITAL = 3
    EMERGENCY_CLINIC = 4
    RELIEF = 5
    WASH_15 = 6
    WASH_20 = 7
    WASH_40 = 8

    # class Labels:
    #     BASECAMP = _('Basecamp')
    #     TELECOM = _('IT & Telecom')
    #     LOGISTICS = _('Logistics')
    #     EMERGENCY_HOSPITAL = _('RCRC Emergency Hospital')
    #     EMERGENCY_CLINIC = _('RCRC Emergency Clinic')
    #     RELIEF = _('Relief')
    #     WASH_15 = _('Wash M15')
    #     WASH_20 = _('Wash MSM20')
    #     WASH_40 = _('Wash M40')


class ERUOwner(models.Model):
    """ A resource that may or may not be deployed """

    national_society_country = models.ForeignKey(
        Country, verbose_name=_('national society country'), null=True, on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('ERUs from a National Society')
        verbose_name_plural = _('ERUs')

    def __str__(self):
        if self.national_society_country.society_name is not None:
            return '%s (%s)' % (self.national_society_country.society_name, self.national_society_country.name)
        return self.national_society_country.name


class ERU(models.Model):
    """ A resource that can be deployed """
    type = EnumIntegerField(ERUType, verbose_name=_('type'), default=0)
    units = models.IntegerField(verbose_name=_('units'), default=0)
    equipment_units = models.IntegerField(verbose_name=_('equipment units'), default=0)
    num_people_deployed = models.IntegerField(
        verbose_name=_('number of people deployed'), default=0, help_text=_('still not used in frontend')
    )
    # where deployed (none if available)
    deployed_to = models.ForeignKey(
        Country, verbose_name=_('country deployed to'), null=True, blank=True, on_delete=models.SET_NULL
    )
    event = models.ForeignKey(Event, verbose_name=_('event'), null=True, blank=True, on_delete=models.SET_NULL)
    appeal = models.ForeignKey(
        Appeal, verbose_name=_('appeal'), null=True, blank=True, on_delete=models.SET_NULL,
        help_text=_('still not used in frontend')
    )
    # links to services
    eru_owner = models.ForeignKey(ERUOwner, verbose_name=_('owner'), on_delete=models.CASCADE)
    supporting_societies = models.CharField(
        verbose_name=_('suuporting societies'), null=True, blank=True, max_length=500, help_text=_('still not used in frontend')
    )
    start_date = models.DateTimeField(verbose_name=_('start date'), null=True, help_text=_('still not used in frontend'))
    end_date = models.DateTimeField(verbose_name=_('end date'), null=True, help_text=_('still not used in frontend'))
    available = models.BooleanField(verbose_name=_('available'), default=False)
    alert_date = models.DateTimeField(verbose_name=_('alert date'), null=True, help_text=_('still not used in frontend'))

    class Meta:
        verbose_name = _('Emergency Response Unit')
        verbose_name_plural = _('Emergency Response Units')

    def __str__(self):
        return str(self.type.label)


class PersonnelDeployment(models.Model):
    country_deployed_to = models.ForeignKey(Country, verbose_name=_('country deployed to'), on_delete=models.CASCADE)
    region_deployed_to = models.ForeignKey(Region, verbose_name=_('region deployed to'), on_delete=models.CASCADE)
    event_deployed_to = models.ForeignKey(
        Event, verbose_name=_('event deployed to'), null=True, blank=True, on_delete=models.SET_NULL
    )
    appeal_deployed_to = models.ForeignKey(
        Appeal, verbose_name=_('appeal deployed to'), null=True, blank=True,
        on_delete=models.SET_NULL, help_text=_('still not used in frontend')
    )
    alert_date = models.DateTimeField(verbose_name=_('alert date'), null=True, help_text=_('still not used in frontend'))
    exp_start_date = models.DateTimeField(
        verbose_name=_('expire start date'), null=True, help_text=_('still not used in frontend')
    )
    end_duration = models.CharField(
        verbose_name=_('end duration'), null=True, blank=True, max_length=100, help_text=_('still not used in frontend')
    )
    start_date = models.DateTimeField(verbose_name=_('start date'), null=True, help_text=_('still not used in frontend'))
    end_date = models.DateTimeField(verbose_name=_('end date'), null=True, help_text=_('still not used in frontend'))
    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name=_('updated at'), auto_now=True)
    previous_update = models.DateTimeField(verbose_name=_('previous update'), null=True, blank=True)
    comments = models.TextField(verbose_name=_('comments'), null=True, blank=True)

    class Meta:
        verbose_name = _('Personnel Deployment')
        verbose_name_plural = _('Personnel Deployments')

    def __str__(self):
        return '%s, %s' % (self.country_deployed_to, self.region_deployed_to)


class DeployedPerson(models.Model):
    start_date = models.DateTimeField(verbose_name=_('start date'), null=True)
    end_date = models.DateTimeField(verbose_name=_('end date'), null=True)
    name = models.CharField(verbose_name=_('name'), null=True, blank=True, max_length=100)
    role = models.CharField(verbose_name=_('role'), null=True, blank=True, max_length=32)

    class Meta:
        verbose_name = _('Deployed Person')
        verbose_name_plural = _('Deployed Persons')

    def __str__(self):
        return '%s - %s' % (self.name, self.role)


class Personnel(DeployedPerson):
    FACT = 'fact'
    HEOP = 'heop'
    RDRT = 'rdrt'
    IFRC = 'ifrc'
    ERU = 'eru'
    RR = 'rr'

    TYPE_CHOICES = (
        (FACT, _('FACT')),
        (HEOP, _('HEOP')),
        (RDRT, _('RDRT')),
        (IFRC, _('IFRC')),
        (ERU, _('ERU HR')),
        (RR, _('Rapid Response')),
    )

    type = models.CharField(verbose_name=_('type'), choices=TYPE_CHOICES, max_length=4)
    country_from = models.ForeignKey(
        Country, verbose_name=_('country from'), related_name='personnel_deployments', null=True, on_delete=models.SET_NULL
    )
    deployment = models.ForeignKey(PersonnelDeployment, verbose_name=_('deployment'), on_delete=models.CASCADE)

    def __str__(self):
        return '%s: %s - %s' % (self.type.upper(), self.name, self.role)

    class Meta:
        verbose_name = _('Personnel')
        verbose_name_plural = _('Personnels')


class PartnerSocietyActivities(models.Model):
    activity = models.CharField(verbose_name=_('activity'), max_length=50)

    def __str__(self):
        return self.activity

    class Meta:
        verbose_name = _('Partner society activity')
        verbose_name_plural = _('Partner society activities')


class PartnerSocietyDeployment(DeployedPerson):
    activity = models.ForeignKey(
        PartnerSocietyActivities, verbose_name=_('activity'), related_name='partner_societies',
        null=True, on_delete=models.CASCADE
    )
    parent_society = models.ForeignKey(
        Country, verbose_name=_('parent society'), related_name='partner_society_members',
        null=True, on_delete=models.SET_NULL
    )
    country_deployed_to = models.ForeignKey(
        Country, verbose_name=_('country deployed to'), related_name='country_partner_deployments',
        null=True, on_delete=models.SET_NULL,
    )
    district_deployed_to = models.ManyToManyField(District, verbose_name=_('district deployed to'))

    class Meta:
        verbose_name = _('Partner Society Deployment')
        verbose_name_plural = _('Partner Society Deployments')

    def __str__(self):
        return '%s deployment in %s' % (self.parent_society, self.country_deployed_to)


class ProgrammeTypes(IntEnum):
    BILATERAL = 0
    MULTILATERAL = 1
    DOMESTIC = 2

    # class Labels:
    #     BILATERAL = _('Bilateral')
    #     MULTILATERAL = _('Multilateral')
    #     DOMESTIC = _('Domestic')


class Sectors(IntEnum):
    HEALTH_AND_CARE = 0
    WATER_SANITATION_AND_HYGIENE_PROMOTION = 1
    RISK_COMMUNICATION_AND_COMMUNITY_ENGAGEMENT_AND_ACCOUNTABILITY = 2
    PROTECTION_GENDER_AND_INCLUSION = 3
    SHELTER = 4
    PLANNING_MONITORING_EVALUATION_REPORTING_AND_INFORMATION_MANAGEMENT = 5
    NATIONAL_SOCIETY_DEVELOPMENT = 6
    LOGISTICS_AND_INFORMATION_TECHNOLOGY = 7
    HUMAN_RESOURCES_AND_DUTY_OF_CARE = 8


class SectorTags(IntEnum):
    HEALTH_AND_CARE = 0
    WATER_SANITATION_AND_HYGIENE_PROMOTION = 1
    RISK_COMMUNICATION_AND_COMMUNITY_ENGAGEMENT_AND_ACCOUNTABILITY = 2
    PROTECTION_GENDER_AND_INCLUSION = 3
    SHELTER = 4
    PLANNING_MONITORING_EVALUATION_REPORTING_AND_INFORMATION_MANAGEMENT = 5
    NATIONAL_SOCIETY_DEVELOPMENT = 6
    LOGISTICS_AND_INFORMATION_TECHNOLOGY = 7
    HUMAN_RESOURCES_AND_DUTY_OF_CARE = 8


class Statuses(IntEnum):
    PLANNED = 0
    ONGOING = 1
    COMPLETED = 2

    # class Labels:
    #     PLANNED = _('Planned')
    #     ONGOING = _('Ongoing')
    #     COMPLETED = _('Completed')


class OperationTypes(IntEnum):
    PROGRAMME = 0
    EMERGENCY_OPERATION = 1

    # class Labels:
    #     PROGRAMME = _('Programme')
    #     EMERGENCY_OPERATION = _('Emergency Operation')


class RegionalProject(models.Model):
    name = models.CharField(verbose_name=_('name'), max_length=100)
    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    modified_at = models.DateTimeField(verbose_name=_('modified at'), auto_now=True)

    class Meta:
        verbose_name = _('Regional Project')
        verbose_name_plural = _('Regional Projects')

    def __str__(self):
        return self.name


class OrganizationalUnits(IntEnum):
    NEPAL_RED_CROSS_HQS = 0
    NRCS_DISTRICT_CHAPTER = 1
    NRCS_SUB_CHAPTER = 2
    JUNIOR_YOUTH_RED_CROSS_COMMUNITY = 3

    class Labels:
        NEPAL_RED_CROSS_HQS = _('Nepal Red Cross HQS')
        NRCS_DISTRICT_CHAPTER = _('NRCS District-Chapter')
        NRCS_SUB_CHAPTER = _('NRCS Sub-Chapter')
        JUNIOR_YOUTH_RED_CROSS_COMMUNITY = _('Junior/Youth Red Cross Community')


class Partners(IntEnum):
    THROUGH_NRCS_HQS = 0
    GOVERNMENT_AGENCIES = 1
    INGO_NGO = 2
    OTHER = 3

    class Labels:
        THROUGH_NRCS_HQS = _('Through NRCS HQS')
        GOVERNMENT_AGENCIES = _('Government Agencies')
        INGO_NGO = _('INGO/NGO')
        OTHER = _('Other')


class Activities(IntEnum):
    CONDUCT_TRAINING_ORIENTATION_ON_COVID_19_PPE_AND_IPC_MEASURE = 0
    BLOOD_DONATION_CAMPAIGN = 1
    ESTABLISH_HEALTH_HELP_DESK = 2
    DISTRIBUTE_PERSONAL_PROTECTIVE_EQUIPMENT_TO_COVID_19_RESPONDERS = 3
    SUPPORT_MEDICAL_EQUIPMENT_AND_MATERIALS = 4
    PROVIDE_PSYCHOSOCIAL_SUPPORT_PSS_TRAINING_ORIENTATION = 5
    UPGRADE_THE_SERVICE_OF_AMBULANCE = 6
    PROVIDE_PSYCHOSOCIAL_FIRST_AID_PFA_TRAINING_ORIENTATION = 7
    CONDUCT_COVID_19_AWARENESS_ACTIVITIES_FOR_COMMUNITY_RISK_COMMUNICATION = 8
    CONDUCT_EPIDEMIC_CONTROL_FOR_VOLUNTEERS_ECV_TRAINING_ORIENTATION_AND_MOBILIZATION = 9
    SETUP_OF_TEMPORARY_QUARANTINE_SPACE = 10
    TRAINING_TO_NRCS_STAFF_AND_VOLUNTEERS_ON_COMMUNITY_BASED_SURVEILLANCE_CONTACT_TRACING = 11
    BROADCAST_RADIO_PROGRAMS_AND_PUBLIC_SERVICE_ANNOUNCEMENT = 12
    COVID_19_PREPAREDNESS_AND_RESPONSE_OPERATION_ASSESSMENT_SURVEYS_EVALUATION = 13
    CONSTRUCTION_REPAIR_AND_MAINTENANCE_ACTIVITY = 14
    DEMONSTRATION_ON_HAND_WASHING_ACTIVITY = 15
    DISTRIBUTE_WASH_MATERIALS = 16
    DISTRIBUTE_INFORMATION_EDUCATION_COMMUNICATION_MATERIALS = 17
    PROVIDE_NON_FOOD_ITEMS_TO_THE_FAMILIES_MOST_AFFECTED_BY_COVID_19 = 18
    PROVIDE_SHELTER_AND_NON_FOOD_RELIEF_ITEMS_TO_THE_FAMILIES_PEOPLE_AFFECTED_BY_COVID_19 = 19
    STAFF_AND_VOLUNTEER_MOBILIZATION_IN_COVID_19_PREPAREDNESS_AND_RESPONSE_OPERATION_FOR_ALL_SECTORS = 20
    SUPPORT_TO_ESTABLISH_UPGRADE_EXPAND_QUARANTINE_FACILITIES_IN_KIND_AND_CASH_SUPPORT_AS_PER_LOCAL_NEED_AND_CONTEXT = 21

    class Labels:
        CONDUCT_TRAINING_ORIENTATION_ON_COVID_19_PPE_AND_IPC_MEASURE = _('Conduct training/orientation on COVID-19 / PPE and IPC measure')
        BLOOD_DONATION_CAMPAIGN = _('Blood donation campaign')
        ESTABLISH_HEALTH_HELP_DESK = _('Establish health/help desk')
        DISTRIBUTE_PERSONAL_PROTECTIVE_EQUIPMENT_TO_COVID_19_RESPONDERS = _('Distribute personal protective equipment to COVID-19 responders')
        SUPPORT_MEDICAL_EQUIPMENT_AND_MATERIALS = _('Support medical equipment and materials')
        PROVIDE_PSYCHOSOCIAL_SUPPORT_PSS_TRAINING_ORIENTATION = _('Provide psychosocial support(PSS) training/orientation')
        UPGRADE_THE_SERVICE_OF_AMBULANCE = _('Upgrade the service of Ambulance')
        PROVIDE_PSYCHOSOCIAL_FIRST_AID_PFA_TRAINING_ORIENTATION = _('Provide psychosocial first aid (PFA)training/orientation')
        CONDUCT_COVID_19_AWARENESS_ACTIVITIES_FOR_COMMUNITY_RISK_COMMUNICATION = _('Conduct COVID-19  awareness activities for community (risk communication)')
        CONDUCT_EPIDEMIC_CONTROL_FOR_VOLUNTEERS_ECV_TRAINING_ORIENTATION_AND_MOBILIZATION = _('Conduct Epidemic Control for Volunteers (ECV) training, orientation and mobilization')
        SETUP_OF_TEMPORARY_QUARANTINE_SPACE = _('Setup of temporary quarantine space')
        TRAINING_TO_NRCS_STAFF_AND_VOLUNTEERS_ON_COMMUNITY_BASED_SURVEILLANCE_CONTACT_TRACING = _('Training to NRCS staff and volunteers on community based surveillance, contact tracing')
        BROADCAST_RADIO_PROGRAMS_AND_PUBLIC_SERVICE_ANNOUNCEMENT = _('Broadcast radio programs and Public Service Announcement')
        COVID_19_PREPAREDNESS_AND_RESPONSE_OPERATION_ASSESSMENT_SURVEYS_EVALUATION = _('COVID-19 preparedness and response operation assessment, surveys, evaluation')
        CONSTRUCTION_REPAIR_AND_MAINTENANCE_ACTIVITY = _('Construction, repair and maintenance activity')
        DEMONSTRATION_ON_HAND_WASHING_ACTIVITY = _('Demonstration on hand washing activity')
        DISTRIBUTE_WASH_MATERIALS = _('Distribute WASH materials')
        DISTRIBUTE_INFORMATION_EDUCATION_COMMUNICATION_MATERIALS = _('Distribute information,education,communication materials')
        PROVIDE_NON_FOOD_ITEMS_TO_THE_FAMILIES_MOST_AFFECTED_BY_COVID_19 = _('Provide non-food items to the families most affected by COVID-19')
        PROVIDE_SHELTER_AND_NON_FOOD_RELIEF_ITEMS_TO_THE_FAMILIES_PEOPLE_AFFECTED_BY_COVID_19 = _('Provide shelter and non-food relief items to the families /people  affected by COVID-19')
        STAFF_AND_VOLUNTEER_MOBILIZATION_IN_COVID_19_PREPAREDNESS_AND_RESPONSE_OPERATION_FOR_ALL_SECTORS = _('Staff and volunteer mobilization in COVID-19 preparedness and response operation (for all sectors)')
        SUPPORT_TO_ESTABLISH_UPGRADE_EXPAND_QUARANTINE_FACILITIES_IN_KIND_AND_CASH_SUPPORT_AS_PER_LOCAL_NEED_AND_CONTEXT = _('Support to establish/upgrade/expand quarantine facilities (in-kind and cash support as per local need and context)')


class Subactivities(IntEnum):
    TRAINING = 0
    ORIENTATION = 1
    DONATION_CAMPAIGN = 2
    DOOR_TO_DOOR_BLOOD_COLLECTION_MECHANISM = 3
    HEALTH_DESK = 4
    HELP_DESK = 5
    FULL_BODY_PPE_SET = 6
    FULL_BODY_APRON = 7
    MASK = 8
    N95_MASK = 9
    DISPOSABLE_EXAMINATION_GLOVES = 10
    GOGGLES_FACE_SHIELD = 11
    RUBBER_BOOT_LONG_TUBE_RUBBER_SHOE = 12
    SHOES_WITH_COVER = 13
    HEAD_COVER = 14
    OTHER = 15
    FIRST_AID_KIT = 16
    PSS_KIT = 17
    EMERGENCY_KIT = 18
    INFRARED_THERMOMETER = 19
    VENTILATOR = 20
    LIQUID_HAND_WASHING_SOAP_WITH_PUMP = 21
    HAND_SANITIZER = 22
    DISINFECT_SOLUTIONS_HYDROCHLORIDE = 23
    DISINFECT_SPRAYER = 24
    PSYCHOSOCIAL_SUPPORT_ORIENTATION = 25
    PSYCHOSOCIAL_SUPPORT_TRAINING = 26
    MATERIAL_SUPPORT = 27
    COMPARTMENT_DIVISION = 28
    PSYCHOSOCIAL_FIRST_AID_TRAINING = 29
    PSYCHOSOCIAL_FIRST_AID_ORIENTATION = 30
    MIKING = 31
    RALLY = 32
    STREET_DRAMA = 33
    DOOR_TO_DOOR_VISIT = 34
    MOBILIZATION = 35
    BLOOD_BANK_EMPLOYEE = 36
    NRCS_EMPLOYEE = 37
    COVID_19_RELATED_NRCS_RADIO_PROGRAM = 38
    EVALUATION = 39
    CONSTRUCTION_OF_HAND_WASHING_STATION = 40
    WATER_SUPPLY_CONNECTION = 41
    DEMONSTRATION_ON_HAND_WASHING = 42
    SOAP = 43
    BUCKET = 44
    HYGIENE_KIT = 45
    MUG = 46
    LEAFLET_PAMPHLETS_HEALTH = 47
    BLANKETS = 48
    TARPAULIN = 49
    BLANKET = 50
    KITCHEN_SET = 51
    VOLUNTEER = 52
    STAFF = 53
    IN_KIND_SUPPORT_MATERIALS = 54

    class Labels:
        TRAINING = _('Training')
        ORIENTATION = _('Orientation')
        DONATION_CAMPAIGN = _('Donation Campaign')
        DOOR_TO_DOOR_BLOOD_COLLECTION_MECHANISM = _('Door to door blood collection mechanism')
        HEALTH_DESK = _('Health Desk')
        HELP_DESK = _('Help Desk')
        FULL_BODY_PPE_SET = _('Full Body PPE Set')
        FULL_BODY_APRON = _('Full Body Apron')
        MASK = _('Mask')
        N95_MASK = _('N95 Mask')
        DISPOSABLE_EXAMINATION_GLOVES = _('Disposable/examination gloves')
        GOGGLES_FACE_SHIELD = _('Goggles/face shield')
        RUBBER_BOOT_LONG_TUBE_RUBBER_SHOE = _('Rubber boot (Long tube rubber shoe)')
        SHOES_WITH_COVER = _('Shoes with cover')
        HEAD_COVER = _('Head cover')
        OTHER = _('Other')
        FIRST_AID_KIT = _('First aid kit')
        PSS_KIT = _('PSS kit')
        EMERGENCY_KIT = _('Emergency Kit')
        INFRARED_THERMOMETER = _('Infrared thermometer')
        VENTILATOR = _('Ventilator')
        LIQUID_HAND_WASHING_SOAP_WITH_PUMP = _('Liquid hand washing soap with pump')
        HAND_SANITIZER = _('Hand Sanitizer')
        DISINFECT_SOLUTIONS_HYDROCHLORIDE = _('Disinfect solutions Hydrochloride')
        DISINFECT_SPRAYER = _('Disinfect sprayer')
        PSYCHOSOCIAL_SUPPORT_ORIENTATION = _('Psychosocial support orientation')
        PSYCHOSOCIAL_SUPPORT_TRAINING = _('Psychosocial support training')
        MATERIAL_SUPPORT = _('Material support')
        COMPARTMENT_DIVISION = _('Compartment division')
        PSYCHOSOCIAL_FIRST_AID_TRAINING = _('Psychosocial first aid training')
        PSYCHOSOCIAL_FIRST_AID_ORIENTATION = _('Psychosocial first aid orientation')
        MIKING = _('Miking')
        RALLY = _('Rally')
        STREET_DRAMA = _('Street Drama')
        DOOR_TO_DOOR_VISIT = _('Door to door visit')
        MOBILIZATION = _('Mobilization')
        BLOOD_BANK_EMPLOYEE = _('Blood bank employee')
        NRCS_EMPLOYEE = _('NRCS employee')
        COVID_19_RELATED_NRCS_RADIO_PROGRAM = _('COVID-19 related NRCS radio program')
        EVALUATION = _('Evaluation')
        CONSTRUCTION_OF_HAND_WASHING_STATION = _('Construction of hand washing station')
        WATER_SUPPLY_CONNECTION = _('Water supply connection')
        DEMONSTRATION_ON_HAND_WASHING = _('Demonstration on hand washing')
        SOAP = _('Soap')
        BUCKET = _('Bucket')
        HYGIENE_KIT = _('Hygiene Kit')
        MUG = _('Mug')
        LEAFLET_PAMPHLETS_HEALTH = _('Leaflet/Pamphlets(Health)')
        BLANKETS = _('Blankets')
        TARPAULIN = _('Tarpaulin')
        BLANKET = _('Blanket')
        KITCHEN_SET = _('Kitchen Set')
        VOLUNTEER = _('Volunteer')
        STAFF = _('Staff')
        IN_KIND_SUPPORT_MATERIALS = _('In- kind support (materials)')


class UnitsMeasurementMetric(IntEnum):
    EVENT = 0
    UNIT = 1
    PIECE = 2
    NUMBER = 3
    LUMP_SUM = 4


class Provinces(IntEnum):
    PROVINCE_1 = 0
    PROVINCE_2 = 1
    BAGMATI = 2
    GANDAKI = 3
    PROVINCE_5 = 4
    KARNALI = 5
    SUDUR_PASHCHIM = 6

    class Labels:
        PROVINCE_1 = _('Province 1')
        PROVINCE_2 = _('Province 2')
        BAGMATI = _('Bagmati')
        GANDAKI = _('Gandaki')
        PROVINCE_5 = _('Province 5')
        KARNALI = _('Karnali')
        SUDUR_PASHCHIM = _('Sudur Pashchim')


class Districts(IntEnum):
    TAPLEJUNG = 0
    PANCHTHAR = 1
    ILAM = 2
    JHAPA = 3
    MORANG = 4
    SUNSARI = 5
    DHANKUTA = 6
    TERHATHUM = 7
    SANKHUWASABHA = 8
    BHOJPUR = 9
    SOLUKHUMBU = 10
    OKHALDHUNGA = 11
    KHOTANG = 12
    UDAYAPUR = 13
    SAPTARI = 14
    SIRAHA = 15
    DHANUSHA = 16
    MAHOTTARI = 17
    SARLAHI = 18
    SINDHULI = 19
    RAMECHHAP = 20
    DOLAKHA = 21
    SINDHUPALCHOK = 22
    KABHREPALANCHOK = 23
    LALITPUR = 24
    BHAKTAPUR = 25
    KATHMANDU = 26
    NUWAKOT = 27
    RASUWA = 28
    DHADING = 29
    MAKAWANPUR = 30
    RAUTAHAT = 31
    BARA = 32
    PARSA = 33
    CHITAWAN = 34
    GORKHA = 35
    LAMJUNG = 36
    TANAHU = 37
    SYANGJA = 38
    KASKI = 39
    MANANG = 40
    MUSTANG = 41
    MYAGDI = 42
    PARBAT = 43
    BAGLUNG = 44
    GULMI = 45
    PALPA = 46
    NAWALPARASI_WEST = 47
    RUPANDEHI = 48
    KAPILBASTU = 49
    ARGHAKHANCHI = 50
    PYUTHAN = 51
    ROLPA = 52
    RUKUM_WEST = 53
    SALYAN = 54
    DANG = 55
    BANKE = 56
    BARDIYA = 57
    SURKHET = 58
    DAILEKH = 59
    JAJARKOT = 60
    DOLPA = 61
    JUMLA = 62
    KALIKOT = 63
    MUGU = 64
    HUMLA = 65
    BAJURA = 66
    BAJHANG = 67
    ACHHAM = 68
    DOTI = 69
    KAILALI = 70
    KANCHANPUR = 71
    DADELDHURA = 72
    BAITADI = 73
    DARCHULA = 74
    NAWALPARASI_EAST = 75
    RUKUM_EAST = 76

    class Labels:
        TAPLEJUNG = _('Taplejung')
        PANCHTHAR = _('Panchthar')
        ILAM = _('Ilam')
        JHAPA = _('Jhapa')
        MORANG = _('Morang')
        SUNSARI = _('Sunsari')
        DHANKUTA = _('Dhankuta')
        TERHATHUM = _('Terhathum')
        SANKHUWASABHA = _('Sankhuwasabha')
        BHOJPUR = _('Bhojpur')
        SOLUKHUMBU = _('Solukhumbu')
        OKHALDHUNGA = _('Okhaldhunga')
        KHOTANG = _('Khotang')
        UDAYAPUR = _('Udayapur')
        SAPTARI = _('Saptari')
        SIRAHA = _('Siraha')
        DHANUSHA = _('Dhanusha')
        MAHOTTARI = _('Mahottari')
        SARLAHI = _('Sarlahi')
        SINDHULI = _('Sindhuli')
        RAMECHHAP = _('Ramechhap')
        DOLAKHA = _('Dolakha')
        SINDHUPALCHOK = _('Sindhupalchok')
        KABHREPALANCHOK = _('Kabhrepalanchok')
        LALITPUR = _('Lalitpur')
        BHAKTAPUR = _('Bhaktapur')
        KATHMANDU = _('Kathmandu')
        NUWAKOT = _('Nuwakot')
        RASUWA = _('Rasuwa')
        DHADING = _('Dhading')
        MAKAWANPUR = _('Makawanpur')
        RAUTAHAT = _('Rautahat')
        BARA = _('Bara')
        PARSA = _('Parsa')
        CHITAWAN = _('Chitawan')
        GORKHA = _('Gorkha')
        LAMJUNG = _('Lamjung')
        TANAHU = _('Tanahu')
        SYANGJA = _('Syangja')
        KASKI = _('Kaski')
        MANANG = _('Manang')
        MUSTANG = _('Mustang')
        MYAGDI = _('Myagdi')
        PARBAT = _('Parbat')
        BAGLUNG = _('Baglung')
        GULMI = _('Gulmi')
        PALPA = _('Palpa')
        NAWALPARASI_WEST = _('Nawalparasi West')
        RUPANDEHI = _('Rupandehi')
        KAPILBASTU = _('Kapilbastu')
        ARGHAKHANCHI = _('Arghakhanchi')
        PYUTHAN = _('Pyuthan')
        ROLPA = _('Rolpa')
        RUKUM_WEST = _('Rukum West')
        SALYAN = _('Salyan')
        DANG = _('Dang')
        BANKE = _('Banke')
        BARDIYA = _('Bardiya')
        SURKHET = _('Surkhet')
        DAILEKH = _('Dailekh')
        JAJARKOT = _('Jajarkot')
        DOLPA = _('Dolpa')
        JUMLA = _('Jumla')
        KALIKOT = _('Kalikot')
        MUGU = _('Mugu')
        HUMLA = _('Humla')
        BAJURA = _('Bajura')
        BAJHANG = _('Bajhang')
        ACHHAM = _('Achham')
        DOTI = _('Doti')
        KAILALI = _('Kailali')
        KANCHANPUR = _('Kanchanpur')
        DADELDHURA = _('Dadeldhura')
        BAITADI = _('Baitadi')
        DARCHULA = _('Darchula')
        NAWALPARASI_EAST = _('Nawalparasi East')
        RUKUM_EAST = _('Rukum East')


class Municipalities(IntEnum):
    AATHRAI_TRIBENI = 0
    MAIWAKHOLA = 1
    MERINGDEN = 2
    MIKWAKHOLA = 3
    PHAKTANGLUNG = 4
    PHUNGLING = 5
    SIDINGBA = 6
    SIRIJANGHA = 7
    PATHIBHARA_YANGWARAK = 8
    FALELUNG = 9
    FALGUNANDA = 10
    HILIHANG = 11
    KUMMAYAK = 12
    MIKLAJUNG = 13
    PHIDIM = 14
    TUMBEWA = 15
    YANGWARAK = 16
    CHULACHULI = 17
    DEUMAI = 18
    FAKPHOKTHUM = 19
    ILAM = 20
    MAI = 21
    MAIJOGMAI = 22
    MANGSEBUNG = 23
    RONG = 24
    SANDAKPUR = 25
    SURYODAYA = 26
    ARJUNDHARA = 27
    BARHADASHI = 28
    BHADRAPUR = 29
    BIRTAMOD = 30
    BUDDHASHANTI = 31
    DAMAK = 32
    GAURADHAHA = 33
    GAURIGANJ = 34
    HALDIBARI = 35
    JHAPA = 36
    KACHANKAWAL = 37
    KAMAL = 38
    KANKAI = 39
    MECHINAGAR = 40
    SHIVASATAXI = 41
    BELBARI = 42
    BIRATNAGAR = 43
    BUDHIGANGA = 44
    DHANPALTHAN = 45
    GRAMTHAN = 46
    JAHADA = 47
    KANEPOKHARI = 48
    KATAHARI = 49
    KERABARI = 50
    LETANG = 51
    PATAHRISHANISHCHARE = 52
    RANGELI = 53
    RATUWAMAI = 54
    SUNDARHARAICHA = 55
    SUNWARSHI = 56
    URALABARI = 57
    BARAH = 58
    BARJU = 59
    BHOKRAHA_NARSINGH = 60
    DEWANGANJ = 61
    DHARAN = 62
    DUHABI = 63
    GADHI = 64
    HARINAGAR = 65
    INARUWA = 66
    ITAHARI = 67
    KOSHI = 68
    RAMDHUNI = 69
    KOSHI_TAPPU_WILDLIFE_RESERVE = 70
    CHAUBISE = 71
    CHHATHAR_JORPATI = 72
    DHANKUTA = 73
    SHAHIDBHUMI = 74
    MAHALAXMI = 75
    PAKHRIBAS = 76
    SANGURIGADHI = 77
    AATHRAI = 78
    CHHATHAR = 79
    LALIGURANS = 80
    MENCHAYAM = 81
    MYANGLUNG = 82
    PHEDAP = 83
    BHOTKHOLA = 84
    CHAINPUR = 85
    CHICHILA = 86
    DHARMADEVI = 87
    KHANDBARI = 88
    MADI = 89
    MAKALU = 90
    PANCHAKHAPAN = 91
    SABHAPOKHARI = 92
    SILICHONG = 93
    AAMCHOWK = 94
    ARUN = 95
    BHOJPUR = 96
    HATUWAGADHI = 97
    PAUWADUNGMA = 98
    RAMPRASAD_RAI = 99
    SALPASILICHHO = 100
    SHADANANDA = 101
    TYAMKEMAIYUNG = 102
    THULUNG_DUDHKOSHI = 103
    DUDHKOSHI = 104
    KHUMBUPASANGLAHMU = 105
    LIKHUPIKE = 106
    MAHAKULUNG = 107
    NECHASALYAN = 108
    SOLUDUDHAKUNDA = 109
    SOTANG = 110
    CHAMPADEVI = 111
    CHISANKHUGADHI = 112
    KHIJIDEMBA = 113
    LIKHU = 114
    MANEBHANJYANG = 115
    MOLUNG = 116
    SIDDHICHARAN = 117
    SUNKOSHI = 118
    AINSELUKHARK = 119
    BARAHAPOKHARI = 120
    DIPRUNG = 121
    HALESI_TUWACHUNG = 122
    JANTEDHUNGA = 123
    KEPILASAGADHI = 124
    KHOTEHANG = 125
    RAWA_BESI = 126
    RUPAKOT_MAJHUWAGADHI = 127
    SAKELA = 128
    BELAKA = 129
    CHAUDANDIGADHI = 130
    KATARI = 131
    RAUTAMAI = 132
    TAPLI = 133
    TRIYUGA = 134
    UDAYAPURGADHI = 135
    AGNISAIR_KRISHNA_SAVARAN = 136
    BALAN_BIHUL = 137
    BELHI_CHAPENA = 138
    BISHNUPUR = 139
    BODE_BARSAIN = 140
    CHHINNAMASTA = 141
    DAKNESHWORI = 142
    HANUMANNAGAR_KANKALINI = 143
    KANCHANRUP = 144
    KHADAK = 145
    MAHADEVA = 146
    RAJBIRAJ = 147
    RUPANI = 148
    SAPTAKOSHI = 149
    SHAMBHUNATH = 150
    SURUNGA = 151
    TILATHI_KOILADI = 152
    TIRAHUT = 153
    ARNAMA = 154
    AURAHI = 155
    BARIYARPATTI = 156
    BHAGAWANPUR = 157
    DHANGADHIMAI = 158
    GOLBAZAR = 159
    KALYANPUR = 160
    KARJANHA = 161
    LAHAN = 162
    LAXMIPUR_PATARI = 163
    MIRCHAIYA = 164
    NARAHA = 165
    NAWARAJPUR = 166
    SAKHUWANANKARKATTI = 167
    SIRAHA = 168
    SUKHIPUR = 169
    AAURAHI = 170
    BATESHWOR = 171
    BIDEHA = 172
    CHHIRESHWORNATH = 173
    DHANAUJI = 174
    DHANUSADHAM = 175
    GANESHMAN_CHARNATH = 176
    HANSAPUR = 177
    JANAKNANDANI = 178
    JANAKPUR = 179
    KAMALA = 180
    LAKSHMINIYA = 181
    MITHILA = 182
    MITHILA_BIHARI = 183
    MUKHIYAPATTI_MUSARMIYA = 184
    NAGARAIN = 185
    SABAILA = 186
    SAHIDNAGAR = 187
    BALWA = 188
    BARDIBAS = 189
    BHANGAHA = 190
    EKDANRA = 191
    GAUSHALA = 192
    JALESWOR = 193
    LOHARPATTI = 194
    MAHOTTARI = 195
    MANRA_SISWA = 196
    MATIHANI = 197
    PIPRA = 198
    RAMGOPALPUR = 199
    SAMSI = 200
    SONAMA = 201
    BAGMATI = 202
    BALARA = 203
    BARAHATHAWA = 204
    BASBARIYA = 205
    BISHNU = 206
    BRAMHAPURI = 207
    CHAKRAGHATTA = 208
    CHANDRANAGAR = 209
    DHANKAUL = 210
    GODAITA = 211
    HARIPUR = 212
    HARIPURWA = 213
    HARIWAN = 214
    ISHWORPUR = 215
    KABILASI = 216
    KAUDENA = 217
    LALBANDI = 218
    MALANGAWA = 219
    PARSA = 220
    RAMNAGAR = 221
    DUDHOULI = 222
    GHANGLEKH = 223
    GOLANJOR = 224
    HARIHARPURGADHI = 225
    KAMALAMAI = 226
    MARIN = 227
    PHIKKAL = 228
    TINPATAN = 229
    DORAMBA = 230
    GOKULGANGA = 231
    KHADADEVI = 232
    LIKHU_TAMAKOSHI = 233
    MANTHALI = 234
    RAMECHHAP = 235
    SUNAPATI = 236
    UMAKUNDA = 237
    BAITESHWOR = 238
    BHIMESHWOR = 239
    BIGU = 240
    GAURISHANKAR = 241
    JIRI = 242
    KALINCHOK = 243
    MELUNG = 244
    SAILUNG = 245
    TAMAKOSHI = 246
    BALEFI = 247
    BARHABISE = 248
    BHOTEKOSHI = 249
    CHAUTARA_SANGACHOK_GADHI = 250
    HELAMBU = 251
    INDRAWATI = 252
    JUGAL = 253
    LISANGKHU_PAKHAR = 254
    MELAMCHI = 255
    PANCHPOKHARI_THANGPAL = 256
    TRIPURASUNDARI = 257
    BANEPA = 258
    BETHANCHOWK = 259
    BHUMLU = 260
    CHAURIDEURALI = 261
    DHULIKHEL = 262
    KHANIKHOLA = 263
    MAHABHARAT = 264
    MANDANDEUPUR = 265
    NAMOBUDDHA = 266
    PANAUTI = 267
    PANCHKHAL = 268
    ROSHI = 269
    TEMAL = 270
    GODAWARI = 271
    KONJYOSOM = 272
    LALITPUR = 273
    MAHANKAL = 274
    BHAKTAPUR = 275
    CHANGUNARAYAN = 276
    MADHYAPUR_THIMI = 277
    SURYABINAYAK = 278
    BUDHANILAKANTHA = 279
    CHANDRAGIRI = 280
    DAKSHINKALI = 281
    GOKARNESHWOR = 282
    KAGESHWORI_MANAHORA = 283
    KATHMANDU = 284
    KIRTIPUR = 285
    NAGARJUN = 286
    SHANKHARAPUR = 287
    TARAKESHWOR = 288
    TOKHA = 289
    BELKOTGADHI = 290
    BIDUR = 291
    DUPCHESHWAR = 292
    KAKANI = 293
    KISPANG = 294
    MEGHANG = 295
    PANCHAKANYA = 296
    SHIVAPURI = 297
    SURYAGADHI = 298
    TADI = 299
    TARKESHWAR = 300
    SHIVAPURI_WATERSHED_AND_WILDLIFE_RESERVE = 301
    LANGTANG_NATIONAL_PARK = 302
    GOSAIKUNDA = 303
    KALIKA = 304
    NAUKUNDA = 305
    PARBATI_KUNDA = 306
    UTTARGAYA = 307
    BENIGHAT_RORANG = 308
    DHUNIBESI = 309
    GAJURI = 310
    GALCHI = 311
    GANGAJAMUNA = 312
    JWALAMUKHI = 313
    KHANIYABASH = 314
    NETRAWATI_DABJONG = 315
    NILAKANTHA = 316
    RUBI_VALLEY = 317
    SIDDHALEK = 318
    THAKRE = 319
    TRIPURA_SUNDARI = 320
    BAKAIYA = 321
    BHIMPHEDI = 322
    HETAUDA = 323
    INDRASAROWAR = 324
    KAILASH = 325
    MAKAWANPURGADHI = 326
    MANAHARI = 327
    RAKSIRANG = 328
    THAHA = 329
    PARSA_WILDLIFE_RESERVE = 330
    CHITAWAN_NATIONAL_PARK = 331
    BAUDHIMAI = 332
    BRINDABAN = 333
    CHANDRAPUR = 334
    DEWAHHI_GONAHI = 335
    DURGA_BHAGWATI = 336
    GADHIMAI = 337
    GARUDA = 338
    GAUR = 339
    GUJARA = 340
    ISHANATH = 341
    KATAHARIYA = 342
    MADHAV_NARAYAN = 343
    MAULAPUR = 344
    PAROHA = 345
    PHATUWA_BIJAYAPUR = 346
    RAJDEVI = 347
    RAJPUR = 348
    YEMUNAMAI = 349
    ADARSHKOTWAL = 350
    BARAGADHI = 351
    BISHRAMPUR = 352
    DEVTAL = 353
    JITPUR_SIMARA = 354
    KALAIYA = 355
    KARAIYAMAI = 356
    KOLHABI = 357
    MAHAGADHIMAI = 358
    NIJGADH = 359
    PACHARAUTA = 360
    PARWANIPUR = 361
    PHETA = 362
    PRASAUNI = 363
    SIMRAUNGADH = 364
    SUWARNA = 365
    BAHUDARAMAI = 366
    BINDABASINI = 367
    BIRGUNJ = 368
    CHHIPAHARMAI = 369
    DHOBINI = 370
    JAGARNATHPUR = 371
    JIRABHAWANI = 372
    KALIKAMAI = 373
    PAKAHAMAINPUR = 374
    PARSAGADHI = 375
    PATERWASUGAULI = 376
    POKHARIYA = 377
    SAKHUWA_PRASAUNI = 378
    THORI = 379
    BHARATPUR = 380
    ICHCHHYAKAMANA = 381
    KHAIRAHANI = 382
    RAPTI = 383
    RATNANAGAR = 384
    AARUGHAT = 385
    AJIRKOT = 386
    BHIMSEN = 387
    CHUM_NUBRI = 388
    DHARCHE = 389
    GANDAKI = 390
    GORKHA = 391
    PALUNGTAR = 392
    SAHID_LAKHAN = 393
    SIRANCHOK = 394
    SULIKOT = 395
    BESISHAHAR = 396
    DORDI = 397
    DUDHPOKHARI = 398
    KWHOLASOTHAR = 399
    MADHYA_NEPAL = 400
    MARSYANGDI = 401
    RAINAS = 402
    SUNDARBAZAR = 403
    ANBUKHAIRENI = 404
    BANDIPUR = 405
    BHANU = 406
    BHIMAD = 407
    BYAS = 408
    DEVGHAT = 409
    GHIRING = 410
    MYAGDE = 411
    RHISHING = 412
    SHUKLAGANDAKI = 413
    AANDHIKHOLA = 414
    ARJUNCHAUPARI = 415
    BHIRKOT = 416
    BIRUWA = 417
    CHAPAKOT = 418
    GALYANG = 419
    HARINAS = 420
    KALIGANDAGI = 421
    PHEDIKHOLA = 422
    PUTALIBAZAR = 423
    WALING = 424
    ANNAPURNA = 425
    MACHHAPUCHCHHRE = 426
    POKHARA_LEKHNATH = 427
    RUPA = 428
    CHAME = 429
    NARPHU = 430
    NASHONG = 431
    NESHYANG = 432
    BARHAGAUN_MUKTIKHSETRA = 433
    DALOME = 434
    GHARAPJHONG = 435
    LOMANTHANG = 436
    THASANG = 437
    BENI = 438
    DHAULAGIRI = 439
    MALIKA = 440
    MANGALA = 441
    RAGHUGANGA = 442
    DHORPATAN_HUNTING_RESERVE = 443
    BIHADI = 444
    JALJALA = 445
    KUSHMA = 446
    MAHASHILA = 447
    MODI = 448
    PAINYU = 449
    PHALEBAS = 450
    BADIGAD = 451
    BAGLUNG = 452
    BARENG = 453
    DHORPATAN = 454
    GALKOT = 455
    JAIMUNI = 456
    KANTHEKHOLA = 457
    NISIKHOLA = 458
    TAMAN_KHOLA = 459
    TARA_KHOLA = 460
    CHANDRAKOT = 461
    CHATRAKOT = 462
    DHURKOT = 463
    GULMIDARBAR = 464
    ISMA = 465
    KALIGANDAKI = 466
    MADANE = 467
    MUSIKOT = 468
    RESUNGA = 469
    RURU = 470
    SATYAWATI = 471
    BAGNASKALI = 472
    MATHAGADHI = 473
    NISDI = 474
    PURBAKHOLA = 475
    RAINADEVI_CHHAHARA = 476
    RAMBHA = 477
    RAMPUR = 478
    RIBDIKOT = 479
    TANSEN = 480
    TINAU = 481
    BARDAGHAT = 482
    PALHI_NANDAN = 483
    PRATAPPUR = 484
    RAMGRAM = 485
    SARAWAL = 486
    SUNWAL = 487
    SUSTA = 488
    BUTWAL = 489
    DEVDAHA = 490
    GAIDAHAWA = 491
    KANCHAN = 492
    KOTAHIMAI = 493
    LUMBINI_SANSKRITIK = 494
    MARCHAWARI = 495
    MAYADEVI = 496
    OMSATIYA = 497
    ROHINI = 498
    SAINAMAINA = 499
    SAMMARIMAI = 500
    SIDDHARTHANAGAR = 501
    SIYARI = 502
    SUDHDHODHAN = 503
    TILLOTAMA = 504
    LUMBINI_SANSKRITIK_DEVELOPMENT_AREA = 505
    BANGANGA = 506
    BIJAYANAGAR = 507
    BUDDHABHUMI = 508
    KAPILBASTU = 509
    KRISHNANAGAR = 510
    MAHARAJGUNJ = 511
    SHIVARAJ = 512
    SUDDHODHAN = 513
    YASHODHARA = 514
    BHUMEKASTHAN = 515
    CHHATRADEV = 516
    MALARANI = 517
    PANINI = 518
    SANDHIKHARKA = 519
    SITGANGA = 520
    AYIRABATI = 521
    GAUMUKHI = 522
    JHIMRUK = 523
    MALLARANI = 524
    MANDAVI = 525
    NAUBAHINI = 526
    PYUTHAN = 527
    SARUMARANI = 528
    SWORGADWARY = 529
    DUIKHOLI = 530
    LUNGRI = 531
    ROLPA = 532
    RUNTIGADI = 533
    SUKIDAHA = 534
    SUNCHHAHARI = 535
    SUWARNABATI = 536
    THAWANG = 537
    TRIBENI = 538
    AATHBISKOT = 539
    BANFIKOT = 540
    CHAURJAHARI = 541
    SANI_BHERI = 542
    BAGCHAUR = 543
    BANGAD_KUPINDE = 544
    CHHATRESHWORI = 545
    DARMA = 546
    DHORCHAUR = 547
    KALIMATI = 548
    KAPURKOT = 549
    KUMAKHMALIKA = 550
    SHARADA = 551
    BABAI = 552
    BANGLACHULI = 553
    DANGISHARAN = 554
    GADHAWA = 555
    GHORAHI = 556
    LAMAHI = 557
    SHANTINAGAR = 558
    TULSIPUR = 559
    BAIJANATH = 560
    DUDUWA = 561
    JANKI = 562
    KHAJURA = 563
    KOHALPUR = 564
    NARAINAPUR = 565
    NEPALGUNJ = 566
    RAPTI_SONARI = 567
    BADHAIYATAL = 568
    BANSAGADHI = 569
    BARBARDIYA = 570
    GERUWA = 571
    GULARIYA = 572
    MADHUWAN = 573
    RAJAPUR = 574
    THAKURBABA = 575
    BARDIYA_NATIONAL_PARK = 576
    BARAHTAL = 577
    BHERIGANGA = 578
    BIRENDRANAGAR = 579
    CHAUKUNE = 580
    CHINGAD = 581
    GURBHAKOT = 582
    LEKBESHI = 583
    PANCHPURI = 584
    SIMTA = 585
    AATHABIS = 586
    BHAGAWATIMAI = 587
    BHAIRABI = 588
    CHAMUNDA_BINDRASAINI = 589
    DULLU = 590
    DUNGESHWOR = 591
    GURANS = 592
    MAHABU = 593
    NARAYAN = 594
    NAUMULE = 595
    THANTIKANDH = 596
    BAREKOT = 597
    BHERI = 598
    CHHEDAGAD = 599
    JUNICHANDE = 600
    KUSE = 601
    SHIWALAYA = 602
    TRIBENI_NALAGAD = 603
    CHHARKA_TANGSONG = 604
    DOLPO_BUDDHA = 605
    JAGADULLA = 606
    KAIKE = 607
    MUDKECHULA = 608
    SHEY_PHOKSUNDO = 609
    THULI_BHERI = 610
    CHANDANNATH = 611
    GUTHICHAUR = 612
    HIMA = 613
    KANAKASUNDARI = 614
    PATRASI = 615
    SINJA = 616
    TATOPANI = 617
    TILA = 618
    KHANDACHAKRA = 619
    MAHAWAI = 620
    NARAHARINATH = 621
    PACHALJHARANA = 622
    PALATA = 623
    RASKOT = 624
    SANNI_TRIBENI = 625
    TILAGUFA = 626
    CHHAYANATH_RARA = 627
    KHATYAD = 628
    MUGUM_KARMARONG = 629
    SORU = 630
    ADANCHULI = 631
    CHANKHELI = 632
    KHARPUNATH = 633
    NAMKHA = 634
    SARKEGAD = 635
    SIMKOT = 636
    TANJAKOT = 637
    BADIMALIKA = 638
    BUDHINANDA = 639
    CHHEDEDAHA = 640
    GAUMUL = 641
    HIMALI = 642
    PANDAV_GUPHA = 643
    SWAMI_KARTIK = 644
    KHAPTAD_NATIONAL_PARK = 645
    BITHADCHIR = 646
    BUNGAL = 647
    CHABISPATHIVERA = 648
    DURGATHALI = 649
    JAYA_PRITHIVI = 650
    KANDA = 651
    KEDARSEU = 652
    KHAPTADCHHANNA = 653
    MASTA = 654
    SURMA = 655
    TALKOT = 656
    THALARA = 657
    BANNIGADHI_JAYAGADH = 658
    CHAURPATI = 659
    DHAKARI = 660
    KAMALBAZAR = 661
    MANGALSEN = 662
    MELLEKH = 663
    PANCHADEWAL_BINAYAK = 664
    RAMAROSHAN = 665
    SANPHEBAGAR = 666
    TURMAKHAD = 667
    ADHARSHA = 668
    BADIKEDAR = 669
    BOGTAN = 670
    DIPAYAL_SILGADI = 671
    JORAYAL = 672
    K_I_SINGH = 673
    PURBICHAUKI = 674
    SAYAL = 675
    SHIKHAR = 676
    BARDAGORIYA = 677
    BHAJANI = 678
    CHURE = 679
    DHANGADHI = 680
    GAURIGANGA = 681
    GHODAGHODI = 682
    JANAKI = 683
    JOSHIPUR = 684
    KAILARI = 685
    LAMKICHUHA = 686
    MOHANYAL = 687
    TIKAPUR = 688
    BEDKOT = 689
    BELAURI = 690
    BELDANDI = 691
    BHIMDATTA = 692
    KRISHNAPUR = 693
    LALJHADI = 694
    MAHAKALI = 695
    PUNARBAS = 696
    SHUKLAPHANTA = 697
    SHUKLAPHANTA_NATIONAL_PARK = 698
    AJAYMERU = 699
    ALITAL = 700
    AMARGADHI = 701
    BHAGESHWAR = 702
    GANAYAPDHURA = 703
    NAWADURGA = 704
    PARASHURAM = 705
    DASHARATHCHANDA = 706
    DILASAINI = 707
    DOGADAKEDAR = 708
    MELAULI = 709
    PANCHESHWAR = 710
    PATAN = 711
    PURCHAUDI = 712
    SHIVANATH = 713
    SIGAS = 714
    SURNAYA = 715
    APIHIMAL = 716
    DUNHU = 717
    LEKAM = 718
    MALIKAARJUN = 719
    MARMA = 720
    NAUGAD = 721
    SHAILYASHIKHAR = 722
    BINAYEE_TRIBENI = 723
    BULINGTAR = 724
    BUNGDIKALI = 725
    DEVCHULI = 726
    GAIDAKOT = 727
    HUPSEKOT = 728
    KAWASOTI = 729
    MADHYABINDU = 730
    BHUME = 731
    PUTHA_UTTARGANGA = 732
    SISNE = 733

    class Labels:
        AATHRAI_TRIBENI = _('Aathrai Tribeni')
        MAIWAKHOLA = _('Maiwakhola')
        MERINGDEN = _('Meringden')
        MIKWAKHOLA = _('Mikwakhola')
        PHAKTANGLUNG = _('Phaktanglung')
        PHUNGLING = _('Phungling')
        SIDINGBA = _('Sidingba')
        SIRIJANGHA = _('Sirijangha')
        PATHIBHARA_YANGWARAK = _('Pathibhara Yangwarak')
        FALELUNG = _('Falelung')
        FALGUNANDA = _('Falgunanda')
        HILIHANG = _('Hilihang')
        KUMMAYAK = _('Kummayak')
        MIKLAJUNG = _('Miklajung')
        PHIDIM = _('Phidim')
        TUMBEWA = _('Tumbewa')
        YANGWARAK = _('Yangwarak')
        CHULACHULI = _('Chulachuli')
        DEUMAI = _('Deumai')
        FAKPHOKTHUM = _('Fakphokthum')
        ILAM = _('Ilam')
        MAI = _('Mai')
        MAIJOGMAI = _('Maijogmai')
        MANGSEBUNG = _('Mangsebung')
        RONG = _('Rong')
        SANDAKPUR = _('Sandakpur')
        SURYODAYA = _('Suryodaya')
        ARJUNDHARA = _('Arjundhara')
        BARHADASHI = _('Barhadashi')
        BHADRAPUR = _('Bhadrapur')
        BIRTAMOD = _('Birtamod')
        BUDDHASHANTI = _('Buddhashanti')
        DAMAK = _('Damak')
        GAURADHAHA = _('Gauradhaha')
        GAURIGANJ = _('Gauriganj')
        HALDIBARI = _('Haldibari')
        JHAPA = _('Jhapa')
        KACHANKAWAL = _('Kachankawal')
        KAMAL = _('Kamal')
        KANKAI = _('Kankai')
        MECHINAGAR = _('Mechinagar')
        SHIVASATAXI = _('Shivasataxi')
        BELBARI = _('Belbari')
        BIRATNAGAR = _('Biratnagar')
        BUDHIGANGA = _('Budhiganga')
        DHANPALTHAN = _('Dhanpalthan')
        GRAMTHAN = _('Gramthan')
        JAHADA = _('Jahada')
        KANEPOKHARI = _('Kanepokhari')
        KATAHARI = _('Katahari')
        KERABARI = _('Kerabari')
        LETANG = _('Letang')
        PATAHRISHANISHCHARE = _('Patahrishanishchare')
        RANGELI = _('Rangeli')
        RATUWAMAI = _('Ratuwamai')
        SUNDARHARAICHA = _('Sundarharaicha')
        SUNWARSHI = _('Sunwarshi')
        URALABARI = _('Uralabari')
        BARAH = _('Barah')
        BARJU = _('Barju')
        BHOKRAHA_NARSINGH = _('Bhokraha Narsingh')
        DEWANGANJ = _('Dewanganj')
        DHARAN = _('Dharan')
        DUHABI = _('Duhabi')
        GADHI = _('Gadhi')
        HARINAGAR = _('Harinagar')
        INARUWA = _('Inaruwa')
        ITAHARI = _('Itahari')
        KOSHI = _('Koshi')
        RAMDHUNI = _('Ramdhuni')
        KOSHI_TAPPU_WILDLIFE_RESERVE = _('Koshi Tappu Wildlife Reserve')
        CHAUBISE = _('Chaubise')
        CHHATHAR_JORPATI = _('Chhathar Jorpati')
        DHANKUTA = _('Dhankuta')
        SHAHIDBHUMI = _('Shahidbhumi')
        MAHALAXMI = _('Mahalaxmi')
        PAKHRIBAS = _('Pakhribas')
        SANGURIGADHI = _('Sangurigadhi')
        AATHRAI = _('Aathrai')
        CHHATHAR = _('Chhathar')
        LALIGURANS = _('Laligurans')
        MENCHAYAM = _('Menchayam')
        MYANGLUNG = _('Myanglung')
        PHEDAP = _('Phedap')
        BHOTKHOLA = _('Bhotkhola')
        CHAINPUR = _('Chainpur')
        CHICHILA = _('Chichila')
        DHARMADEVI = _('Dharmadevi')
        KHANDBARI = _('Khandbari')
        MADI = _('Madi')
        MAKALU = _('Makalu')
        PANCHAKHAPAN = _('Panchakhapan')
        SABHAPOKHARI = _('Sabhapokhari')
        SILICHONG = _('Silichong')
        AAMCHOWK = _('Aamchowk')
        ARUN = _('Arun')
        BHOJPUR = _('Bhojpur')
        HATUWAGADHI = _('Hatuwagadhi')
        PAUWADUNGMA = _('Pauwadungma')
        RAMPRASAD_RAI = _('Ramprasad Rai')
        SALPASILICHHO = _('Salpasilichho')
        SHADANANDA = _('Shadananda')
        TYAMKEMAIYUNG = _('Tyamkemaiyung')
        THULUNG_DUDHKOSHI = _('Thulung Dudhkoshi')
        DUDHKOSHI = _('Dudhkoshi')
        KHUMBUPASANGLAHMU = _('Khumbupasanglahmu')
        LIKHUPIKE = _('Likhupike')
        MAHAKULUNG = _('Mahakulung')
        NECHASALYAN = _('Nechasalyan')
        SOLUDUDHAKUNDA = _('Solududhakunda')
        SOTANG = _('Sotang')
        CHAMPADEVI = _('Champadevi')
        CHISANKHUGADHI = _('Chisankhugadhi')
        KHIJIDEMBA = _('Khijidemba')
        LIKHU = _('Likhu')
        MANEBHANJYANG = _('Manebhanjyang')
        MOLUNG = _('Molung')
        SIDDHICHARAN = _('Siddhicharan')
        SUNKOSHI = _('Sunkoshi')
        AINSELUKHARK = _('Ainselukhark')
        BARAHAPOKHARI = _('Barahapokhari')
        DIPRUNG = _('Diprung')
        HALESI_TUWACHUNG = _('Halesi Tuwachung')
        JANTEDHUNGA = _('Jantedhunga')
        KEPILASAGADHI = _('Kepilasagadhi')
        KHOTEHANG = _('Khotehang')
        RAWA_BESI = _('Rawa Besi')
        RUPAKOT_MAJHUWAGADHI = _('Rupakot Majhuwagadhi')
        SAKELA = _('Sakela')
        BELAKA = _('Belaka')
        CHAUDANDIGADHI = _('Chaudandigadhi')
        KATARI = _('Katari')
        RAUTAMAI = _('Rautamai')
        TAPLI = _('Tapli')
        TRIYUGA = _('Triyuga')
        UDAYAPURGADHI = _('Udayapurgadhi')
        AGNISAIR_KRISHNA_SAVARAN = _('Agnisair Krishna Savaran')
        BALAN_BIHUL = _('Balan Bihul')
        BELHI_CHAPENA = _('Belhi Chapena')
        BISHNUPUR = _('Bishnupur')
        BODE_BARSAIN = _('Bode Barsain')
        CHHINNAMASTA = _('Chhinnamasta')
        DAKNESHWORI = _('Dakneshwori')
        HANUMANNAGAR_KANKALINI = _('Hanumannagar Kankalini')
        KANCHANRUP = _('Kanchanrup')
        KHADAK = _('Khadak')
        MAHADEVA = _('Mahadeva')
        RAJBIRAJ = _('Rajbiraj')
        RUPANI = _('Rupani')
        SAPTAKOSHI = _('Saptakoshi')
        SHAMBHUNATH = _('Shambhunath')
        SURUNGA = _('Surunga')
        TILATHI_KOILADI = _('Tilathi Koiladi')
        TIRAHUT = _('Tirahut')
        ARNAMA = _('Arnama')
        AURAHI = _('Aurahi')
        BARIYARPATTI = _('Bariyarpatti')
        BHAGAWANPUR = _('Bhagawanpur')
        DHANGADHIMAI = _('Dhangadhimai')
        GOLBAZAR = _('Golbazar')
        KALYANPUR = _('Kalyanpur')
        KARJANHA = _('Karjanha')
        LAHAN = _('Lahan')
        LAXMIPUR_PATARI = _('Laxmipur Patari')
        MIRCHAIYA = _('Mirchaiya')
        NARAHA = _('Naraha')
        NAWARAJPUR = _('Nawarajpur')
        SAKHUWANANKARKATTI = _('Sakhuwanankarkatti')
        SIRAHA = _('Siraha')
        SUKHIPUR = _('Sukhipur')
        AAURAHI = _('Aaurahi')
        BATESHWOR = _('Bateshwor')
        BIDEHA = _('Bideha')
        CHHIRESHWORNATH = _('Chhireshwornath')
        DHANAUJI = _('Dhanauji')
        DHANUSADHAM = _('Dhanusadham')
        GANESHMAN_CHARNATH = _('Ganeshman Charnath')
        HANSAPUR = _('Hansapur')
        JANAKNANDANI = _('Janaknandani')
        JANAKPUR = _('Janakpur')
        KAMALA = _('Kamala')
        LAKSHMINIYA = _('Lakshminiya')
        MITHILA = _('Mithila')
        MITHILA_BIHARI = _('Mithila Bihari')
        MUKHIYAPATTI_MUSARMIYA = _('Mukhiyapatti Musarmiya')
        NAGARAIN = _('Nagarain')
        SABAILA = _('Sabaila')
        SAHIDNAGAR = _('Sahidnagar')
        BALWA = _('Balwa')
        BARDIBAS = _('Bardibas')
        BHANGAHA = _('Bhangaha')
        EKDANRA = _('Ekdanra')
        GAUSHALA = _('Gaushala')
        JALESWOR = _('Jaleswor')
        LOHARPATTI = _('Loharpatti')
        MAHOTTARI = _('Mahottari')
        MANRA_SISWA = _('Manra Siswa')
        MATIHANI = _('Matihani')
        PIPRA = _('Pipra')
        RAMGOPALPUR = _('Ramgopalpur')
        SAMSI = _('Samsi')
        SONAMA = _('Sonama')
        BAGMATI = _('Bagmati')
        BALARA = _('Balara')
        BARAHATHAWA = _('Barahathawa')
        BASBARIYA = _('Basbariya')
        BISHNU = _('Bishnu')
        BRAMHAPURI = _('Bramhapuri')
        CHAKRAGHATTA = _('Chakraghatta')
        CHANDRANAGAR = _('Chandranagar')
        DHANKAUL = _('Dhankaul')
        GODAITA = _('Godaita')
        HARIPUR = _('Haripur')
        HARIPURWA = _('Haripurwa')
        HARIWAN = _('Hariwan')
        ISHWORPUR = _('Ishworpur')
        KABILASI = _('Kabilasi')
        KAUDENA = _('Kaudena')
        LALBANDI = _('Lalbandi')
        MALANGAWA = _('Malangawa')
        PARSA = _('Parsa')
        RAMNAGAR = _('Ramnagar')
        DUDHOULI = _('Dudhouli')
        GHANGLEKH = _('Ghanglekh')
        GOLANJOR = _('Golanjor')
        HARIHARPURGADHI = _('Hariharpurgadhi')
        KAMALAMAI = _('Kamalamai')
        MARIN = _('Marin')
        PHIKKAL = _('Phikkal')
        TINPATAN = _('Tinpatan')
        DORAMBA = _('Doramba')
        GOKULGANGA = _('Gokulganga')
        KHADADEVI = _('Khadadevi')
        LIKHU_TAMAKOSHI = _('Likhu Tamakoshi')
        MANTHALI = _('Manthali')
        RAMECHHAP = _('Ramechhap')
        SUNAPATI = _('Sunapati')
        UMAKUNDA = _('Umakunda')
        BAITESHWOR = _('Baiteshwor')
        BHIMESHWOR = _('Bhimeshwor')
        BIGU = _('Bigu')
        GAURISHANKAR = _('Gaurishankar')
        JIRI = _('Jiri')
        KALINCHOK = _('Kalinchok')
        MELUNG = _('Melung')
        SAILUNG = _('Sailung')
        TAMAKOSHI = _('Tamakoshi')
        BALEFI = _('Balefi')
        BARHABISE = _('Barhabise')
        BHOTEKOSHI = _('Bhotekoshi')
        CHAUTARA_SANGACHOK_GADHI = _('Chautara SangachokGadhi')
        HELAMBU = _('Helambu')
        INDRAWATI = _('Indrawati')
        JUGAL = _('Jugal')
        LISANGKHU_PAKHAR = _('Lisangkhu Pakhar')
        MELAMCHI = _('Melamchi')
        PANCHPOKHARI_THANGPAL = _('Panchpokhari Thangpal')
        TRIPURASUNDARI = _('Tripurasundari')
        BANEPA = _('Banepa')
        BETHANCHOWK = _('Bethanchowk')
        BHUMLU = _('Bhumlu')
        CHAURIDEURALI = _('Chaurideurali')
        DHULIKHEL = _('Dhulikhel')
        KHANIKHOLA = _('Khanikhola')
        MAHABHARAT = _('Mahabharat')
        MANDANDEUPUR = _('Mandandeupur')
        NAMOBUDDHA = _('Namobuddha')
        PANAUTI = _('Panauti')
        PANCHKHAL = _('Panchkhal')
        ROSHI = _('Roshi')
        TEMAL = _('Temal')
        GODAWARI = _('Godawari')
        KONJYOSOM = _('Konjyosom')
        LALITPUR = _('Lalitpur')
        MAHANKAL = _('Mahankal')
        BHAKTAPUR = _('Bhaktapur')
        CHANGUNARAYAN = _('Changunarayan')
        MADHYAPUR_THIMI = _('Madhyapur Thimi')
        SURYABINAYAK = _('Suryabinayak')
        BUDHANILAKANTHA = _('Budhanilakantha')
        CHANDRAGIRI = _('Chandragiri')
        DAKSHINKALI = _('Dakshinkali')
        GOKARNESHWOR = _('Gokarneshwor')
        KAGESHWORI_MANAHORA = _('Kageshwori Manahora')
        KATHMANDU = _('Kathmandu')
        KIRTIPUR = _('Kirtipur')
        NAGARJUN = _('Nagarjun')
        SHANKHARAPUR = _('Shankharapur')
        TARAKESHWOR = _('Tarakeshwor')
        TOKHA = _('Tokha')
        BELKOTGADHI = _('Belkotgadhi')
        BIDUR = _('Bidur')
        DUPCHESHWAR = _('Dupcheshwar')
        KAKANI = _('Kakani')
        KISPANG = _('Kispang')
        MEGHANG = _('Meghang')
        PANCHAKANYA = _('Panchakanya')
        SHIVAPURI = _('Shivapuri')
        SURYAGADHI = _('Suryagadhi')
        TADI = _('Tadi')
        TARKESHWAR = _('Tarkeshwar')
        SHIVAPURI_WATERSHED_AND_WILDLIFE_RESERVE = _('Shivapuri Watershed and Wildlife Reserve')
        LANGTANG_NATIONAL_PARK = _('Langtang National Park')
        GOSAIKUNDA = _('Gosaikunda')
        KALIKA = _('Kalika')
        NAUKUNDA = _('Naukunda')
        PARBATI_KUNDA = _('Parbati Kunda')
        UTTARGAYA = _('Uttargaya')
        BENIGHAT_RORANG = _('Benighat Rorang')
        DHUNIBESI = _('Dhunibesi')
        GAJURI = _('Gajuri')
        GALCHI = _('Galchi')
        GANGAJAMUNA = _('Gangajamuna')
        JWALAMUKHI = _('Jwalamukhi')
        KHANIYABASH = _('Khaniyabash')
        NETRAWATI_DABJONG = _('Netrawati Dabjong')
        NILAKANTHA = _('Nilakantha')
        RUBI_VALLEY = _('Rubi Valley')
        SIDDHALEK = _('Siddhalek')
        THAKRE = _('Thakre')
        TRIPURA_SUNDARI = _('Tripura Sundari')
        BAKAIYA = _('Bakaiya')
        BHIMPHEDI = _('Bhimphedi')
        HETAUDA = _('Hetauda')
        INDRASAROWAR = _('Indrasarowar')
        KAILASH = _('Kailash')
        MAKAWANPURGADHI = _('Makawanpurgadhi')
        MANAHARI = _('Manahari')
        RAKSIRANG = _('Raksirang')
        THAHA = _('Thaha')
        PARSA_WILDLIFE_RESERVE = _('Parsa Wildlife Reserve')
        CHITAWAN_NATIONAL_PARK = _('Chitawan National Park')
        BAUDHIMAI = _('Baudhimai')
        BRINDABAN = _('Brindaban')
        CHANDRAPUR = _('Chandrapur')
        DEWAHHI_GONAHI = _('Dewahhi Gonahi')
        DURGA_BHAGWATI = _('Durga Bhagwati')
        GADHIMAI = _('Gadhimai')
        GARUDA = _('Garuda')
        GAUR = _('Gaur')
        GUJARA = _('Gujara')
        ISHANATH = _('Ishanath')
        KATAHARIYA = _('Katahariya')
        MADHAV_NARAYAN = _('Madhav Narayan')
        MAULAPUR = _('Maulapur')
        PAROHA = _('Paroha')
        PHATUWA_BIJAYAPUR = _('Phatuwa Bijayapur')
        RAJDEVI = _('Rajdevi')
        RAJPUR = _('Rajpur')
        YEMUNAMAI = _('Yemunamai')
        ADARSHKOTWAL = _('Adarshkotwal')
        BARAGADHI = _('Baragadhi')
        BISHRAMPUR = _('Bishrampur')
        DEVTAL = _('Devtal')
        JITPUR_SIMARA = _('Jitpur Simara')
        KALAIYA = _('Kalaiya')
        KARAIYAMAI = _('Karaiyamai')
        KOLHABI = _('Kolhabi')
        MAHAGADHIMAI = _('Mahagadhimai')
        NIJGADH = _('Nijgadh')
        PACHARAUTA = _('Pacharauta')
        PARWANIPUR = _('Parwanipur')
        PHETA = _('Pheta')
        PRASAUNI = _('Prasauni')
        SIMRAUNGADH = _('Simraungadh')
        SUWARNA = _('Suwarna')
        BAHUDARAMAI = _('Bahudaramai')
        BINDABASINI = _('Bindabasini')
        BIRGUNJ = _('Birgunj')
        CHHIPAHARMAI = _('Chhipaharmai')
        DHOBINI = _('Dhobini')
        JAGARNATHPUR = _('Jagarnathpur')
        JIRABHAWANI = _('Jirabhawani')
        KALIKAMAI = _('Kalikamai')
        PAKAHAMAINPUR = _('Pakahamainpur')
        PARSAGADHI = _('Parsagadhi')
        PATERWASUGAULI = _('Paterwasugauli')
        POKHARIYA = _('Pokhariya')
        SAKHUWA_PRASAUNI = _('SakhuwaPrasauni')
        THORI = _('Thori')
        BHARATPUR = _('Bharatpur')
        ICHCHHYAKAMANA = _('Ichchhyakamana')
        KHAIRAHANI = _('Khairahani')
        RAPTI = _('Rapti')
        RATNANAGAR = _('Ratnanagar')
        AARUGHAT = _('Aarughat')
        AJIRKOT = _('Ajirkot')
        BHIMSEN = _('Bhimsen')
        CHUM_NUBRI = _('Chum Nubri')
        DHARCHE = _('Dharche')
        GANDAKI = _('Gandaki')
        GORKHA = _('Gorkha')
        PALUNGTAR = _('Palungtar')
        SAHID_LAKHAN = _('Sahid Lakhan')
        SIRANCHOK = _('Siranchok')
        SULIKOT = _('Sulikot')
        BESISHAHAR = _('Besishahar')
        DORDI = _('Dordi')
        DUDHPOKHARI = _('Dudhpokhari')
        KWHOLASOTHAR = _('Kwholasothar')
        MADHYA_NEPAL = _('MadhyaNepal')
        MARSYANGDI = _('Marsyangdi')
        RAINAS = _('Rainas')
        SUNDARBAZAR = _('Sundarbazar')
        ANBUKHAIRENI = _('Anbukhaireni')
        BANDIPUR = _('Bandipur')
        BHANU = _('Bhanu')
        BHIMAD = _('Bhimad')
        BYAS = _('Byas')
        DEVGHAT = _('Devghat')
        GHIRING = _('Ghiring')
        MYAGDE = _('Myagde')
        RHISHING = _('Rhishing')
        SHUKLAGANDAKI = _('Shuklagandaki')
        AANDHIKHOLA = _('Aandhikhola')
        ARJUNCHAUPARI = _('Arjunchaupari')
        BHIRKOT = _('Bhirkot')
        BIRUWA = _('Biruwa')
        CHAPAKOT = _('Chapakot')
        GALYANG = _('Galyang')
        HARINAS = _('Harinas')
        KALIGANDAGI = _('Kaligandagi')
        PHEDIKHOLA = _('Phedikhola')
        PUTALIBAZAR = _('Putalibazar')
        WALING = _('Waling')
        ANNAPURNA = _('Annapurna')
        MACHHAPUCHCHHRE = _('Machhapuchchhre')
        POKHARA_LEKHNATH = _('Pokhara Lekhnath')
        RUPA = _('Rupa')
        CHAME = _('Chame')
        NARPHU = _('Narphu')
        NASHONG = _('Nashong')
        NESHYANG = _('Neshyang')
        BARHAGAUN_MUKTIKHSETRA = _('Barhagaun Muktikhsetra')
        DALOME = _('Dalome')
        GHARAPJHONG = _('Gharapjhong')
        LOMANTHANG = _('Lomanthang')
        THASANG = _('Thasang')
        BENI = _('Beni')
        DHAULAGIRI = _('Dhaulagiri')
        MALIKA = _('Malika')
        MANGALA = _('Mangala')
        RAGHUGANGA = _('Raghuganga')
        DHORPATAN_HUNTING_RESERVE = _('Dhorpatan Hunting Reserve')
        BIHADI = _('Bihadi')
        JALJALA = _('Jaljala')
        KUSHMA = _('Kushma')
        MAHASHILA = _('Mahashila')
        MODI = _('Modi')
        PAINYU = _('Painyu')
        PHALEBAS = _('Phalebas')
        BADIGAD = _('Badigad')
        BAGLUNG = _('Baglung')
        BARENG = _('Bareng')
        DHORPATAN = _('Dhorpatan')
        GALKOT = _('Galkot')
        JAIMUNI = _('Jaimuni')
        KANTHEKHOLA = _('Kanthekhola')
        NISIKHOLA = _('Nisikhola')
        TAMAN_KHOLA = _('Taman Khola')
        TARA_KHOLA = _('Tara Khola')
        CHANDRAKOT = _('Chandrakot')
        CHATRAKOT = _('Chatrakot')
        DHURKOT = _('Dhurkot')
        GULMIDARBAR = _('Gulmidarbar')
        ISMA = _('Isma')
        KALIGANDAKI = _('Kaligandaki')
        MADANE = _('Madane')
        MUSIKOT = _('Musikot')
        RESUNGA = _('Resunga')
        RURU = _('Ruru')
        SATYAWATI = _('Satyawati')
        BAGNASKALI = _('Bagnaskali')
        MATHAGADHI = _('Mathagadhi')
        NISDI = _('Nisdi')
        PURBAKHOLA = _('Purbakhola')
        RAINADEVI_CHHAHARA = _('Rainadevi Chhahara')
        RAMBHA = _('Rambha')
        RAMPUR = _('Rampur')
        RIBDIKOT = _('Ribdikot')
        TANSEN = _('Tansen')
        TINAU = _('Tinau')
        BARDAGHAT = _('Bardaghat')
        PALHI_NANDAN = _('Palhi Nandan')
        PRATAPPUR = _('Pratappur')
        RAMGRAM = _('Ramgram')
        SARAWAL = _('Sarawal')
        SUNWAL = _('Sunwal')
        SUSTA = _('Susta')
        BUTWAL = _('Butwal')
        DEVDAHA = _('Devdaha')
        GAIDAHAWA = _('Gaidahawa')
        KANCHAN = _('Kanchan')
        KOTAHIMAI = _('Kotahimai')
        LUMBINI_SANSKRITIK = _('Lumbini Sanskritik')
        MARCHAWARI = _('Marchawari')
        MAYADEVI = _('Mayadevi')
        OMSATIYA = _('Omsatiya')
        ROHINI = _('Rohini')
        SAINAMAINA = _('Sainamaina')
        SAMMARIMAI = _('Sammarimai')
        SIDDHARTHANAGAR = _('Siddharthanagar')
        SIYARI = _('Siyari')
        SUDHDHODHAN = _('Sudhdhodhan')
        TILLOTAMA = _('Tillotama')
        LUMBINI_SANSKRITIK_DEVELOPMENT_AREA = _('Lumbini Sanskritik Development Area')
        BANGANGA = _('Banganga')
        BIJAYANAGAR = _('Bijayanagar')
        BUDDHABHUMI = _('Buddhabhumi')
        KAPILBASTU = _('Kapilbastu')
        KRISHNANAGAR = _('Krishnanagar')
        MAHARAJGUNJ = _('Maharajgunj')
        SHIVARAJ = _('Shivaraj')
        SUDDHODHAN = _('Suddhodhan')
        YASHODHARA = _('Yashodhara')
        BHUMEKASTHAN = _('Bhumekasthan')
        CHHATRADEV = _('Chhatradev')
        MALARANI = _('Malarani')
        PANINI = _('Panini')
        SANDHIKHARKA = _('Sandhikharka')
        SITGANGA = _('Sitganga')
        AYIRABATI = _('Ayirabati')
        GAUMUKHI = _('Gaumukhi')
        JHIMRUK = _('Jhimruk')
        MALLARANI = _('Mallarani')
        MANDAVI = _('Mandavi')
        NAUBAHINI = _('Naubahini')
        PYUTHAN = _('Pyuthan')
        SARUMARANI = _('Sarumarani')
        SWORGADWARY = _('Sworgadwary')
        DUIKHOLI = _('Duikholi')
        LUNGRI = _('Lungri')
        ROLPA = _('Rolpa')
        RUNTIGADI = _('Runtigadi')
        SUKIDAHA = _('Sukidaha')
        SUNCHHAHARI = _('Sunchhahari')
        SUWARNABATI = _('Suwarnabati')
        THAWANG = _('Thawang')
        TRIBENI = _('Tribeni')
        AATHBISKOT = _('Aathbiskot')
        BANFIKOT = _('Banfikot')
        CHAURJAHARI = _('Chaurjahari')
        SANI_BHERI = _('Sani Bheri')
        BAGCHAUR = _('Bagchaur')
        BANGAD_KUPINDE = _('Bangad Kupinde')
        CHHATRESHWORI = _('Chhatreshwori')
        DARMA = _('Darma')
        DHORCHAUR = _('Dhorchaur')
        KALIMATI = _('Kalimati')
        KAPURKOT = _('Kapurkot')
        KUMAKHMALIKA = _('Kumakhmalika')
        SHARADA = _('Sharada')
        BABAI = _('Babai')
        BANGLACHULI = _('Banglachuli')
        DANGISHARAN = _('Dangisharan')
        GADHAWA = _('Gadhawa')
        GHORAHI = _('Ghorahi')
        LAMAHI = _('Lamahi')
        SHANTINAGAR = _('Shantinagar')
        TULSIPUR = _('Tulsipur')
        BAIJANATH = _('Baijanath')
        DUDUWA = _('Duduwa')
        JANKI = _('Janki')
        KHAJURA = _('Khajura')
        KOHALPUR = _('Kohalpur')
        NARAINAPUR = _('Narainapur')
        NEPALGUNJ = _('Nepalgunj')
        RAPTI_SONARI = _('Rapti Sonari')
        BADHAIYATAL = _('Badhaiyatal')
        BANSAGADHI = _('Bansagadhi')
        BARBARDIYA = _('Barbardiya')
        GERUWA = _('Geruwa')
        GULARIYA = _('Gulariya')
        MADHUWAN = _('Madhuwan')
        RAJAPUR = _('Rajapur')
        THAKURBABA = _('Thakurbaba')
        BARDIYA_NATIONAL_PARK = _('Bardiya National Park')
        BARAHTAL = _('Barahtal')
        BHERIGANGA = _('Bheriganga')
        BIRENDRANAGAR = _('Birendranagar')
        CHAUKUNE = _('Chaukune')
        CHINGAD = _('Chingad')
        GURBHAKOT = _('Gurbhakot')
        LEKBESHI = _('Lekbeshi')
        PANCHPURI = _('Panchpuri')
        SIMTA = _('Simta')
        AATHABIS = _('Aathabis')
        BHAGAWATIMAI = _('Bhagawatimai')
        BHAIRABI = _('Bhairabi')
        CHAMUNDA_BINDRASAINI = _('Chamunda Bindrasaini')
        DULLU = _('Dullu')
        DUNGESHWOR = _('Dungeshwor')
        GURANS = _('Gurans')
        MAHABU = _('Mahabu')
        NARAYAN = _('Narayan')
        NAUMULE = _('Naumule')
        THANTIKANDH = _('Thantikandh')
        BAREKOT = _('Barekot')
        BHERI = _('Bheri')
        CHHEDAGAD = _('Chhedagad')
        JUNICHANDE = _('Junichande')
        KUSE = _('Kuse')
        SHIWALAYA = _('Shiwalaya')
        TRIBENI_NALAGAD = _('Tribeni Nalagad')
        CHHARKA_TANGSONG = _('Chharka Tangsong')
        DOLPO_BUDDHA = _('Dolpo Buddha')
        JAGADULLA = _('Jagadulla')
        KAIKE = _('Kaike')
        MUDKECHULA = _('Mudkechula')
        SHEY_PHOKSUNDO = _('Shey Phoksundo')
        THULI_BHERI = _('Thuli Bheri')
        CHANDANNATH = _('Chandannath')
        GUTHICHAUR = _('Guthichaur')
        HIMA = _('Hima')
        KANAKASUNDARI = _('Kanakasundari')
        PATRASI = _('Patrasi')
        SINJA = _('Sinja')
        TATOPANI = _('Tatopani')
        TILA = _('Tila')
        KHANDACHAKRA = _('Khandachakra')
        MAHAWAI = _('Mahawai')
        NARAHARINATH = _('Naraharinath')
        PACHALJHARANA = _('Pachaljharana')
        PALATA = _('Palata')
        RASKOT = _('Raskot')
        SANNI_TRIBENI = _('Sanni Tribeni')
        TILAGUFA = _('Tilagufa')
        CHHAYANATH_RARA = _('Chhayanath Rara')
        KHATYAD = _('Khatyad')
        MUGUM_KARMARONG = _('Mugum Karmarong')
        SORU = _('Soru')
        ADANCHULI = _('Adanchuli')
        CHANKHELI = _('Chankheli')
        KHARPUNATH = _('Kharpunath')
        NAMKHA = _('Namkha')
        SARKEGAD = _('Sarkegad')
        SIMKOT = _('Simkot')
        TANJAKOT = _('Tanjakot')
        BADIMALIKA = _('Badimalika')
        BUDHINANDA = _('Budhinanda')
        CHHEDEDAHA = _('Chhededaha')
        GAUMUL = _('Gaumul')
        HIMALI = _('Himali')
        PANDAV_GUPHA = _('Pandav Gupha')
        SWAMI_KARTIK = _('Swami Kartik')
        KHAPTAD_NATIONAL_PARK = _('Khaptad National Park')
        BITHADCHIR = _('Bithadchir')
        BUNGAL = _('Bungal')
        CHABISPATHIVERA = _('Chabispathivera')
        DURGATHALI = _('Durgathali')
        JAYA_PRITHIVI = _('JayaPrithivi')
        KANDA = _('Kanda')
        KEDARSEU = _('Kedarseu')
        KHAPTADCHHANNA = _('Khaptadchhanna')
        MASTA = _('Masta')
        SURMA = _('Surma')
        TALKOT = _('Talkot')
        THALARA = _('Thalara')
        BANNIGADHI_JAYAGADH = _('Bannigadhi Jayagadh')
        CHAURPATI = _('Chaurpati')
        DHAKARI = _('Dhakari')
        KAMALBAZAR = _('Kamalbazar')
        MANGALSEN = _('Mangalsen')
        MELLEKH = _('Mellekh')
        PANCHADEWAL_BINAYAK = _('Panchadewal Binayak')
        RAMAROSHAN = _('Ramaroshan')
        SANPHEBAGAR = _('Sanphebagar')
        TURMAKHAD = _('Turmakhad')
        ADHARSHA = _('Adharsha')
        BADIKEDAR = _('Badikedar')
        BOGTAN = _('Bogtan')
        DIPAYAL_SILGADI = _('Dipayal Silgadi')
        JORAYAL = _('Jorayal')
        K_I_SINGH = _('K I Singh')
        PURBICHAUKI = _('Purbichauki')
        SAYAL = _('Sayal')
        SHIKHAR = _('Shikhar')
        BARDAGORIYA = _('Bardagoriya')
        BHAJANI = _('Bhajani')
        CHURE = _('Chure')
        DHANGADHI = _('Dhangadhi')
        GAURIGANGA = _('Gauriganga')
        GHODAGHODI = _('Ghodaghodi')
        JANAKI = _('Janaki')
        JOSHIPUR = _('Joshipur')
        KAILARI = _('Kailari')
        LAMKICHUHA = _('Lamkichuha')
        MOHANYAL = _('Mohanyal')
        TIKAPUR = _('Tikapur')
        BEDKOT = _('Bedkot')
        BELAURI = _('Belauri')
        BELDANDI = _('Beldandi')
        BHIMDATTA = _('Bhimdatta')
        KRISHNAPUR = _('Krishnapur')
        LALJHADI = _('Laljhadi')
        MAHAKALI = _('Mahakali')
        PUNARBAS = _('Punarbas')
        SHUKLAPHANTA = _('Shuklaphanta')
        SHUKLAPHANTA_NATIONAL_PARK = _('Shuklaphanta National Park')
        AJAYMERU = _('Ajaymeru')
        ALITAL = _('Alital')
        AMARGADHI = _('Amargadhi')
        BHAGESHWAR = _('Bhageshwar')
        GANAYAPDHURA = _('Ganayapdhura')
        NAWADURGA = _('Nawadurga')
        PARASHURAM = _('Parashuram')
        DASHARATHCHANDA = _('Dasharathchanda')
        DILASAINI = _('Dilasaini')
        DOGADAKEDAR = _('Dogadakedar')
        MELAULI = _('Melauli')
        PANCHESHWAR = _('Pancheshwar')
        PATAN = _('Patan')
        PURCHAUDI = _('Purchaudi')
        SHIVANATH = _('Shivanath')
        SIGAS = _('Sigas')
        SURNAYA = _('Surnaya')
        APIHIMAL = _('Apihimal')
        DUNHU = _('Dunhu')
        LEKAM = _('Lekam')
        MALIKAARJUN = _('Malikaarjun')
        MARMA = _('Marma')
        NAUGAD = _('Naugad')
        SHAILYASHIKHAR = _('Shailyashikhar')
        BINAYEE_TRIBENI = _('Binayee Tribeni')
        BULINGTAR = _('Bulingtar')
        BUNGDIKALI = _('Bungdikali')
        DEVCHULI = _('Devchuli')
        GAIDAKOT = _('Gaidakot')
        HUPSEKOT = _('Hupsekot')
        KAWASOTI = _('Kawasoti')
        MADHYABINDU = _('Madhyabindu')
        BHUME = _('Bhume')
        PUTHA_UTTARGANGA = _('Putha Uttarganga')
        SISNE = _('Sisne')


class DeliveryServicePlaces(IntEnum):
    COMMUNITY = 0
    INSTITUTION = 1
    QUARANTINE_SITE = 2
    PORT_OF_ENTRY = 3
    HOLDING_CENTER = 4
    ISOLATION_CENTER = 5
    OFFICE = 6
    ORGANIZATION = 7
    HEALTH_SERVICE_CENTER = 8
    BLOOD_TRANSFUSION_SERVICE = 9
    EYE_CARE_CENTER = 10
    AMBULANCE_SERVICE = 11
    HEALTH_HELP_DESK_SERVICE = 12
    CENTRAL_WAREHOUSE = 13
    REGIONAL_WAREHOUSE = 14
    SUB_REGIONAL_WAREHOUSE = 15
    OTHER = 16

    class Labels:
        COMMUNITY = _('Community')
        INSTITUTION = _('Institution')
        QUARANTINE_SITE = _('Quarantine Site')
        PORT_OF_ENTRY = _('Port of Entry')
        HOLDING_CENTER = _('Holding Center')
        ISOLATION_CENTER = _('Isolation Center')
        OFFICE = _('Office')
        ORGANIZATION = _('Organization')
        HEALTH_SERVICE_CENTER = _('Health Service Center')
        BLOOD_TRANSFUSION_SERVICE = _('Blood Transfusion Service')
        EYE_CARE_CENTER = _('Eye Care Center')
        AMBULANCE_SERVICE = _('Ambulance Service')
        HEALTH_HELP_DESK_SERVICE = _('Health/Help-desk Service')
        CENTRAL_WAREHOUSE = _('Central Warehouse')
        REGIONAL_WAREHOUSE = _('Regional Warehouse')
        SUB_REGIONAL_WAREHOUSE = _('Sub-Regional Warehouse')
        OTHER = _('Other')


class BeneficiaryTypes(IntEnum):
    INDIVIDUAL = 0
    HOUSEHOLD = 1
    NRCS_VOLUNTEER = 2
    NRCS_EMPLOYEE = 3
    OTHER_VOLUNTEER = 4
    GOVERNMENT_STAFF = 5
    OTHER = 6

    class Labels:
        INDIVIDUAL = _('Individual')
        HOUSEHOLD = _('Household')
        NRCS_VOLUNTEER = _('NRCS Volunteer')
        NRCS_EMPLOYEE = _('NRCS Employee')
        OTHER_VOLUNTEER = _('Other Volunteer')
        GOVERNMENT_STAFF = _('Government Staff')
        OTHER = _('Other')


class Project(models.Model):
    modified_at = models.DateTimeField(verbose_name=_('modified at'), auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('user'), null=True, blank=True, on_delete=models.SET_NULL,
    )  # user who created this project
    reporting_ns = models.ForeignKey(
        Country, verbose_name=_('reporting national society'), on_delete=models.CASCADE,
        related_name='ns_projects',
    )  # this is the national society that is reporting the project
    project_country = models.ForeignKey(
        Country, verbose_name=_('country'), on_delete=models.CASCADE,
        null=True,  # NOTE: Added due to migrations issue
        related_name='projects',
    )  # this is the country where the project is actually taking place
    project_districts = models.ManyToManyField(
        District, verbose_name=_('districts'),
    )  # this is the district where the project is actually taking place
    event = models.ForeignKey(
        Event, verbose_name=_('event'), null=True, blank=True, on_delete=models.SET_NULL,
    )  # this is the current operation
    dtype = models.ForeignKey(DisasterType, verbose_name=_('disaster type'), null=True, blank=True, on_delete=models.SET_NULL)
    name = models.TextField(verbose_name=_('name'))
    programme_type = EnumIntegerField(ProgrammeTypes, verbose_name=_('programme type'))
    primary_sector = EnumIntegerField(Sectors, verbose_name=_('sector'))
    secondary_sectors = ArrayField(
        EnumIntegerField(SectorTags), verbose_name=_('tags'), default=list, blank=True,
    )
    operation_type = EnumIntegerField(OperationTypes, verbose_name=_('operation type'))
    start_date = models.DateField(verbose_name=_('start date'))
    end_date = models.DateField(verbose_name=_('end date'))
    budget_amount = models.IntegerField(verbose_name=_('budget amount'), null=True, blank=True)
    actual_expenditure = models.IntegerField(verbose_name=_('actual expenditure'), null=True, blank=True)
    status = EnumIntegerField(Statuses, verbose_name=_('status'))
    organizational_unit = EnumIntegerField(OrganizationalUnits, verbose_name=_('organizational unit'), default=0)
    partner = EnumIntegerField(Partners, verbose_name=_('partner'), default=0)
    activity = EnumIntegerField(Activities, verbose_name=_('activity'), default=0)
    subactivity = EnumIntegerField(Subactivities, verbose_name=_('subactivity'), default=0)
    units_measurement_metric = EnumIntegerField(UnitsMeasurementMetric, verbose_name=_('units measurement metric'), default=0)
    units_quantity = models.IntegerField(verbose_name=_('units quantity'), default=-1)
    where_province = EnumIntegerField(Provinces, verbose_name=_('where province'), default=0)
    where_district = EnumIntegerField(Districts, verbose_name=_('where district'), default=0)
    where_municipality = EnumIntegerField(Municipalities, verbose_name=_('where municipality'), null=True, blank=True)
    where_ward = models.IntegerField(verbose_name=_('where ward'), null=True, blank=True)
    where_delivery_service_place = EnumIntegerField(DeliveryServicePlaces, verbose_name=_('where delivery service place'), default=0)
    where_delivery_service_name = models.TextField(verbose_name=_('where delivery service name'), null=True, blank=True)
    beneficiary_type = EnumIntegerField(BeneficiaryTypes, verbose_name=_('beneficiary type'), default=0)

    # Target Metric
    target_male = models.IntegerField(verbose_name=_('target male'), null=True, blank=True)
    target_female = models.IntegerField(verbose_name=_('target female'), null=True, blank=True)
    target_other = models.IntegerField(verbose_name=_('target other'), null=True, blank=True)
    target_total = models.IntegerField(verbose_name=_('target total'), null=True, blank=True)
    target_lgbtiq = models.IntegerField(verbose_name=_('target LGBTIQ'), null=True, blank=True)

    # Reached Metric
    reached_male = models.IntegerField(verbose_name=_('reached male'), null=True, blank=True)
    reached_female = models.IntegerField(verbose_name=_('reached female'), null=True, blank=True)
    reached_other = models.IntegerField(verbose_name=_('reached other'), null=True, blank=True)
    reached_total = models.IntegerField(verbose_name=_('reached total'), null=True, blank=True)
    reached_lgbtiq = models.IntegerField(verbose_name=_('reached LGBTIQ'), null=True, blank=True)

    target_lgbtiq_00_05 = models.IntegerField(verbose_name=_('target lgbtiq 00 05'), null=True, blank=True)
    target_lgbtiq_06_12 = models.IntegerField(verbose_name=_('target lgbtiq 06 12'), null=True, blank=True)
    target_lgbtiq_13_17 = models.IntegerField(verbose_name=_('target lgbtiq 13 17'), null=True, blank=True)
    target_lgbtiq_18_29 = models.IntegerField(verbose_name=_('target lgbtiq 18 29'), null=True, blank=True)
    target_lgbtiq_30_39 = models.IntegerField(verbose_name=_('target lgbtiq 30 39'), null=True, blank=True)
    target_lgbtiq_40_49 = models.IntegerField(verbose_name=_('target lgbtiq 40 49'), null=True, blank=True)
    target_lgbtiq_50_59 = models.IntegerField(verbose_name=_('target lgbtiq 50 59'), null=True, blank=True)
    target_lgbtiq_60_69 = models.IntegerField(verbose_name=_('target lgbtiq 60 69'), null=True, blank=True)
    target_lgbtiq_70_79 = models.IntegerField(verbose_name=_('target lgbtiq 70 79'), null=True, blank=True)
    target_lgbtiq_80_plus = models.IntegerField(verbose_name=_('target lgbtiq 80 plus'), null=True, blank=True)
    target_female_00_05 = models.IntegerField(verbose_name=_('target female 00 05'), null=True, blank=True)
    target_female_06_12 = models.IntegerField(verbose_name=_('target female 06 12'), null=True, blank=True)
    target_female_13_17 = models.IntegerField(verbose_name=_('target female 13 17'), null=True, blank=True)
    target_female_18_29 = models.IntegerField(verbose_name=_('target female 18 29'), null=True, blank=True)
    target_female_30_39 = models.IntegerField(verbose_name=_('target female 30 39'), null=True, blank=True)
    target_female_40_49 = models.IntegerField(verbose_name=_('target female 40 49'), null=True, blank=True)
    target_female_50_59 = models.IntegerField(verbose_name=_('target female 50 59'), null=True, blank=True)
    target_female_60_69 = models.IntegerField(verbose_name=_('target female 60 69'), null=True, blank=True)
    target_female_70_79 = models.IntegerField(verbose_name=_('target female 70 79'), null=True, blank=True)
    target_female_80_plus = models.IntegerField(verbose_name=_('target female 80 plus'), null=True, blank=True)
    target_male_00_05 = models.IntegerField(verbose_name=_('target male 00 05'), null=True, blank=True)
    target_male_06_12 = models.IntegerField(verbose_name=_('target male 06 12'), null=True, blank=True)
    target_male_13_17 = models.IntegerField(verbose_name=_('target male 13 17'), null=True, blank=True)
    target_male_18_29 = models.IntegerField(verbose_name=_('target male 18 29'), null=True, blank=True)
    target_male_30_39 = models.IntegerField(verbose_name=_('target male 30 39'), null=True, blank=True)
    target_male_40_49 = models.IntegerField(verbose_name=_('target male 40 49'), null=True, blank=True)
    target_male_50_59 = models.IntegerField(verbose_name=_('target male 50 59'), null=True, blank=True)
    target_male_60_69 = models.IntegerField(verbose_name=_('target male 60 69'), null=True, blank=True)
    target_male_70_79 = models.IntegerField(verbose_name=_('target male 70 79'), null=True, blank=True)
    target_male_80_plus = models.IntegerField(verbose_name=_('target male 80 plus'), null=True, blank=True)
    target_pregnant_women = models.IntegerField(verbose_name=_('target pregnant women'), null=True, blank=True)
    target_people_with_disability = models.IntegerField(verbose_name=_('target people with disability'), null=True, blank=True)
    reached_lgbtiq_00_05 = models.IntegerField(verbose_name=_('reached lgbtiq 00 05'), null=True, blank=True)
    reached_lgbtiq_06_12 = models.IntegerField(verbose_name=_('reached lgbtiq 06 12'), null=True, blank=True)
    reached_lgbtiq_13_17 = models.IntegerField(verbose_name=_('reached lgbtiq 13 17'), null=True, blank=True)
    reached_lgbtiq_18_29 = models.IntegerField(verbose_name=_('reached lgbtiq 18 29'), null=True, blank=True)
    reached_lgbtiq_30_39 = models.IntegerField(verbose_name=_('reached lgbtiq 30 39'), null=True, blank=True)
    reached_lgbtiq_40_49 = models.IntegerField(verbose_name=_('reached lgbtiq 40 49'), null=True, blank=True)
    reached_lgbtiq_50_59 = models.IntegerField(verbose_name=_('reached lgbtiq 50 59'), null=True, blank=True)
    reached_lgbtiq_60_69 = models.IntegerField(verbose_name=_('reached lgbtiq 60 69'), null=True, blank=True)
    reached_lgbtiq_70_79 = models.IntegerField(verbose_name=_('reached lgbtiq 70 79'), null=True, blank=True)
    reached_lgbtiq_80_plus = models.IntegerField(verbose_name=_('reached lgbtiq 80 plus'), null=True, blank=True)
    reached_female_00_05 = models.IntegerField(verbose_name=_('reached female 00 05'), null=True, blank=True)
    reached_female_06_12 = models.IntegerField(verbose_name=_('reached female 06 12'), null=True, blank=True)
    reached_female_13_17 = models.IntegerField(verbose_name=_('reached female 13 17'), null=True, blank=True)
    reached_female_18_29 = models.IntegerField(verbose_name=_('reached female 18 29'), null=True, blank=True)
    reached_female_30_39 = models.IntegerField(verbose_name=_('reached female 30 39'), null=True, blank=True)
    reached_female_40_49 = models.IntegerField(verbose_name=_('reached female 40 49'), null=True, blank=True)
    reached_female_50_59 = models.IntegerField(verbose_name=_('reached female 50 59'), null=True, blank=True)
    reached_female_60_69 = models.IntegerField(verbose_name=_('reached female 60 69'), null=True, blank=True)
    reached_female_70_79 = models.IntegerField(verbose_name=_('reached female 70 79'), null=True, blank=True)
    reached_female_80_plus = models.IntegerField(verbose_name=_('reached female 80 plus'), null=True, blank=True)
    reached_male_00_05 = models.IntegerField(verbose_name=_('reached male 00 05'), null=True, blank=True)
    reached_male_06_12 = models.IntegerField(verbose_name=_('reached male 06 12'), null=True, blank=True)
    reached_male_13_17 = models.IntegerField(verbose_name=_('reached male 13 17'), null=True, blank=True)
    reached_male_18_29 = models.IntegerField(verbose_name=_('reached male 18 29'), null=True, blank=True)
    reached_male_30_39 = models.IntegerField(verbose_name=_('reached male 30 39'), null=True, blank=True)
    reached_male_40_49 = models.IntegerField(verbose_name=_('reached male 40 49'), null=True, blank=True)
    reached_male_50_59 = models.IntegerField(verbose_name=_('reached male 50 59'), null=True, blank=True)
    reached_male_60_69 = models.IntegerField(verbose_name=_('reached male 60 69'), null=True, blank=True)
    reached_male_70_79 = models.IntegerField(verbose_name=_('reached male 70 79'), null=True, blank=True)
    reached_male_80_plus = models.IntegerField(verbose_name=_('reached male 80 plus'), null=True, blank=True)
    reached_pregnant_women = models.IntegerField(verbose_name=_('reached pregnant women'), null=True, blank=True)
    reached_people_with_disability = models.IntegerField(verbose_name=_('reached people with disability'), null=True, blank=True)

    regional_project = models.ForeignKey(
        RegionalProject, verbose_name=_('regional project'), null=True, blank=True, on_delete=models.SET_NULL
    )
    visibility = models.CharField(
        max_length=32, verbose_name=_('visibility'),
        choices=VisibilityCharChoices.CHOICES, default=VisibilityCharChoices.PUBLIC
    )

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __str__(self):
        if self.reporting_ns is None:
            postfix = None
        else:
            postfix = self.reporting_ns.society_name
        return '%s (%s)' % (self.name, postfix)

    def get_secondary_sectors_display(self):
        choices_dict = dict(make_hashable(SectorTags.choices()))
        return [
            force_str(choices_dict.get(make_hashable(value), value), strings_only=True)
            for value in self.secondary_sectors or []
        ]

    @classmethod
    def get_for(cls, user, queryset=None):
        qs = cls.objects.all() if queryset is None else queryset
        if user.is_authenticated:
            if user.email and user.email.endswith('@ifrc.org'):
                return qs
            return qs.exclude(visibility=VisibilityCharChoices.IFRC)
        return qs.filter(visibility=VisibilityCharChoices.PUBLIC)


class ProjectImport(models.Model):
    """
    Track Project Imports (For Django Admin Panel)
    """
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILURE = 'failure'
    STATUS_CHOICES = (
        (PENDING, _('Pending')),
        (SUCCESS, _('Success')),
        (FAILURE, _('Failure')),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('created by'), on_delete=models.SET_NULL, null=True,
    )  # user who created this project import
    created_at = models.DateTimeField(verbose_name=_('created at'), auto_now_add=True)
    projects_created = models.ManyToManyField(Project, verbose_name=_('projects created'))
    message = models.TextField(verbose_name=_('message'))
    status = models.CharField(verbose_name=_('status'), max_length=10, choices=STATUS_CHOICES, default=PENDING)
    file = models.FileField(verbose_name=_('file'), upload_to='project-imports/')

    class Meta:
        verbose_name = _('Project Import')
        verbose_name_plural = _('Projects Import')

    def __str__(self):
        return f'Project Import {self.get_status_display()}:{self.created_at}'


class ERUReadiness(models.Model):
    """ ERU Readiness concerning personnel and equipment """
    national_society = models.ForeignKey(
        Country, verbose_name=_('national society'), null=True, blank=True, on_delete=models.SET_NULL
    )
    ERU_type = EnumIntegerField(ERUType, verbose_name=_('ERU type'), default=0)
    is_personnel = models.BooleanField(verbose_name=_('is personnel?'), default=False)
    is_equipment = models.BooleanField(verbose_name=_('is equipment?'), default=False)
    updated_at = models.DateTimeField(verbose_name=_('updated at'), auto_now=True)

    class Meta:
        ordering = ('updated_at', 'national_society', )
        verbose_name = _('ERU Readiness')
        verbose_name_plural = _('NS-es ERU Readiness')

    def __str__(self):
        if self.national_society is None:
            name = None
        else:
            name = self.national_society
        return '%s (%s)' % (str(self.ERU_type.label), name)


###############################################################################
####################### Deprecated tables ##################################### noqa: E266
# https://github.com/IFRCGo/go-frontend/issues/335
# NOTE: Translation is skipped for Deprecated tables
###############################################################################


class Heop(models.Model):
    """ A deployment of a head officer"""
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL)
    dtype = models.ForeignKey(DisasterType, null=True, blank=True, on_delete=models.SET_NULL)

    person = models.CharField(null=True, blank=True, max_length=100)
    role = models.CharField(default='HeOps', null=True, blank=True, max_length=32)
    comments = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'HeOp'
        verbose_name_plural = 'HeOps'

    def __str__(self):
        return '%s (%s) %s - %s' % (self.person, self.country,
                                    datetime.strftime(self.start_date, DATE_FORMAT),
                                    datetime.strftime(self.end_date, DATE_FORMAT))


class Fact(models.Model):
    """ A FACT resource"""
    start_date = models.DateTimeField(null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL)
    dtype = models.ForeignKey(DisasterType, null=True, blank=True, on_delete=models.SET_NULL)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s %s' % (self.country, datetime.strftime(self.start_date, DATE_FORMAT))

    class Meta:
        verbose_name = 'FACT'
        verbose_name_plural = 'FACTs'


class Rdrt(models.Model):
    """ An RDRT/RIT resource"""
    start_date = models.DateTimeField(null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, null=True, blank=True, on_delete=models.SET_NULL)
    dtype = models.ForeignKey(DisasterType, null=True, blank=True, on_delete=models.SET_NULL)
    comments = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s %s' % (self.country, datetime.strftime(self.start_date, DATE_FORMAT))

    class Meta:
        verbose_name = 'RDRT/RIT'
        verbose_name_plural = 'RDRTs/RITs'


class FactPerson(DeployedPerson):
    society_deployed_from = models.CharField(null=True, blank=True, max_length=100)
    fact = models.ForeignKey(Fact, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'FACT Person'
        verbose_name_plural = 'FACT People'


class RdrtPerson(DeployedPerson):
    society_deployed_from = models.CharField(null=True, blank=True, max_length=100)
    rdrt = models.ForeignKey(Rdrt, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'RDRT/RIT Person'
        verbose_name_plural = 'RDRT/RIT People'
