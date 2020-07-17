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
    WASH = 0
    PGI = 1
    CEA = 2
    MIGRATION = 3
    HEALTH = 4
    DRR = 5
    SHELTER = 6
    NS_STRENGTHENING = 7
    EDUCATION = 8
    LIVELIHOODS_AND_BASIC_NEEDS = 9

    class Labels:
        WASH = _('WASH')
        PGI = _('PGI')
        CEA = _('CEA')
        MIGRATION = _('Migration')
        HEALTH = _('Health')
        DRR = _('DRR')
        SHELTER = _('Shelter')
        NS_STRENGTHENING = _('NS Strengthening')
        EDUCATION = _('Education')
        LIVELIHOODS_AND_BASIC_NEEDS = _('Livelihoods and basic needs')


class SectorTags(IntEnum):
    WASH = 0
    PGI = 1
    CEA = 2
    MIGRATION = 3
    DRR = 5
    SHELTER = 6
    NS_STRENGTHENING = 7
    EDUCATION = 8
    LIVELIHOODS_AND_BASIC_NEEDS = 9
    RECOVERY = 10
    INTERNAL_DISPLACEMENT = 11
    HEALTH_PUBLIC = 4
    HEALTH_CLINICAL = 12
    COVID_19 = 13
    RCCE = 14

    class Labels:
        WASH = _('WASH')
        PGI = _('PGI')
        CEA = _('CEA')
        MIGRATION = _('Migration')
        DRR = _('DRR')
        SHELTER = _('Shelter')
        NS_STRENGTHENING = _('NS Strengthening')
        EDUCATION = _('Education')
        LIVELIHOODS_AND_BASIC_NEEDS = _('Livelihoods and basic needs')
        RECOVERY = _('Recovery')
        INTERNAL_DISPLACEMENT = _('Internal displacement')
        HEALTH_PUBLIC = _('Health (public)')
        HEALTH_CLINICAL = _('Health (clinical)')
        COVID_19 = _('COVID-19')
        RCCE = _('RCCE')


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


class Partners(IntEnum):
    THROUGH_NRCS_HQS = 0
    GOVERNMENT_AGENCIES = 1
    INGO_NGO = 2
    OTHER = 3


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
    SUDURPASCHIM = 6


class Districts(IntEnum):
    BHOJPUR = 0
    DHANKUTA = 1
    ILAM = 2
    JHAPA = 3
    KHOTANG = 4
    MORANG = 5
    OKHALDHUNGA = 6
    PANCHTHAR = 7
    SANKHUWASABHA = 8
    SOLUKHUMBU = 9
    SUNSARI = 10
    TAPLEJUNG = 11
    TERHATHUM = 12
    UDAYAPUR = 13
    BARA = 14
    DHANUSHA = 15
    BHAKTAPUR = 16
    CHITAWAN = 17
    DHADING = 18
    DOLAKHA = 19
    KATHMANDU = 20
    KAVREPALANCHOK = 21
    LALITPUR = 22
    MAKAWANPUR = 23
    NUWAKOT = 24
    RAMECHHAP = 25
    RASUWA = 26
    SINDHULI = 27
    SINDHUPALCHOK = 28
    BAGLUNG = 29
    GORKHA = 30
    ARGHAKHANCHI = 31
    BANKE = 32
    DAILEKH = 33
    DOLPA = 34
    ACHHAM = 35
    BAITADI = 36


class Municipalities(IntEnum):
    AAMCHOWK = 0
    ARUN = 1
    BHOJPUR = 2
    HATUWAGADHI = 3
    PAUWADUNGMA = 4
    RAMPRASAD_RAI = 5
    SALPASILICHHO = 6
    SHADANANDA = 7
    TEMKEMAIYUNG = 8
    CHAUBISE = 9
    CHHATHAR_JORPATI = 10
    DHANKUTA = 11
    MAHALAXMI = 12
    PAKHRIBAS = 13
    SAHIDBHUMI = 14
    SANGURIGADHI = 15
    CHULACHULI = 16
    DEUMAI = 17
    FAKPHOKTHUM = 18
    ILLAM = 19
    MAI = 20
    MAIJOGMAI = 21
    MANGSEBUNG = 22
    RONG = 23
    SANDAKPUR = 24
    SURYODAYA = 25
    ARJUNDHARA = 26
    BARHADASHI = 27
    BHADRAPUR = 28
    BIRTAMOD = 29
    BUDDHASHANTI = 30
    DAMAK = 31
    GAURADHAHA = 32
    GAURIGANJ = 33
    HALDIBARI = 34
    JHAPA = 35
    KAMAL = 36
    KANKAI = 37
    MECHINAGAR = 38
    SHIVASATAXI = 39
    KACHANKAWAL = 40
    FALELUNG = 41
    FALGUNANDA = 42
    HILIHANG = 43
    KUMMAYAK = 44
    MIKLAJUNG = 45
    PHIDIM = 46
    TUMBEWA = 47
    YANGWARAK = 48
    KHUMBUPASANGLAHMU = 49
    LIKHUPIKE = 50
    MAHAKULUNG = 51
    MAPYADUDHKOSHI = 52
    NECHASALYAN = 53
    SOLUDUDHAKUNDA = 54
    SOTANG = 55
    THULUNG_DUDHKOSHI = 56
    AATHRAI_TRIBENI = 57
    MAIWAKHOLA = 58
    MERINGDEN = 59
    MIKWAKHOLA = 60
    PATHIVARA_YANGWARAK = 61
    PHAKTANGLUNG = 62
    PHUNGLING = 63
    SIDINGBA = 64
    SIRIJANGHA = 65
    AAURAHI = 66
    BATESHWOR = 67
    BHAKTAPUR = 68
    CHANGUNARAYAN = 69
    MADHYAPUR_THIMI = 70
    SURYABINAYAK = 71
    BHARATPUR = 72
    ICHCHHYAKAMANA = 73
    BENIGHAT_RORANG = 74
    DHUNIBESI = 75
    GAJURI = 76
    GALCHI = 77
    GANGAJAMUNA = 78
    JWALAMUKHI = 79
    KHANIYABASH = 80
    NETRAWATI = 81
    NILAKANTHA = 82
    RUBI_VALLEY = 83
    SIDDHALEK = 84
    THAKRE = 85
    TRIPURA_SUNDARI = 86
    BELKOTGADHI = 87
    BIDUR = 88
    DUPCHESHWAR = 89
    KAKANI = 90
    KISPANG = 91
    LIKHU = 92
    MEGHANG = 93
    PANCHAKANYA = 94
    SHIVAPURI = 95
    SURYAGADHI = 96
    TADI = 97
    TARKESHWAR = 98
    GOSAIKUNDA = 99
    KALIKA = 100
    NAUKUNDA = 101
    PARBATI_KUNDA = 102
    UTTARGAYA = 103
    DUDHOULI = 104
    GHANGLEKH = 105
    GOLANJOR = 106
    HARIHARPURGADHI = 107
    KAMALAMAI = 108
    MARIN = 109
    PHIKKAL = 110
    SUNKOSHI = 111
    TINPATAN = 112
    BADIGAD = 113
    BAGLUNG = 114
    AARUGHAT = 115
    AJIRKOT = 116
    BHUMEKASTHAN = 117
    CHHATRADEV = 118
    BAIJANATH = 119
    DUDUWA = 120
    AATHABIS = 121
    BHAGAWATIMAI = 122
    CHHARKA_TANGSONG = 123
    DOLPO_BUDDHA = 124
    BANNIGADHI_JAYAGADH = 125
    CHAURPATI = 126
    DASHARATHCHANDA = 127
    DILASAINI = 128


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


class BeneficiaryTypes(IntEnum):
    INDIVIDUAL = 0
    HOUSEHOLD = 1
    NRCS_VOLUNTEER = 2
    NRCS_EMPLOYEE = 3
    OTHER_VOLUNTEER = 4
    GOVERNMENT_STAFF = 5
    OTHER = 6


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
    where_municipality = EnumIntegerField(Municipalities, verbose_name=_('where municipality'), default=0)
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
