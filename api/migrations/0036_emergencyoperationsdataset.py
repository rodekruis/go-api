# Generated by Django 2.0.12 on 2019-12-12 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_fieldreport_ns_request_assistance'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyOperationsDataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_validated', models.BooleanField(default=False, help_text='Did anyone check the editable data?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('raw_file_name', models.TextField(blank=True, null=True)),
                ('raw_file_url', models.TextField(blank=True, null=True)),
                ('raw_appeal_launch_date', models.TextField(blank=True, null=True)),
                ('raw_appeal_number', models.TextField(blank=True, null=True)),
                ('raw_category_allocated', models.TextField(blank=True, null=True)),
                ('raw_date_of_issue', models.TextField(blank=True, null=True)),
                ('raw_dref_allocated', models.TextField(blank=True, null=True)),
                ('raw_expected_end_date', models.TextField(blank=True, null=True)),
                ('raw_expected_time_frame', models.TextField(blank=True, null=True)),
                ('raw_glide_number', models.TextField(blank=True, null=True)),
                ('raw_num_of_people_affected', models.TextField(blank=True, null=True)),
                ('raw_num_of_people_to_be_assisted', models.TextField(blank=True, null=True)),
                ('raw_disaster_risk_reduction_female', models.TextField(blank=True, null=True)),
                ('raw_disaster_risk_reduction_male', models.TextField(blank=True, null=True)),
                ('raw_disaster_risk_reduction_people_reached', models.TextField(blank=True, null=True)),
                ('raw_disaster_risk_reduction_people_targeted', models.TextField(blank=True, null=True)),
                ('raw_disaster_risk_reduction_requirements', models.TextField(blank=True, null=True)),
                ('raw_health_female', models.TextField(blank=True, null=True)),
                ('raw_health_male', models.TextField(blank=True, null=True)),
                ('raw_health_people_reached', models.TextField(blank=True, null=True)),
                ('raw_health_people_targeted', models.TextField(blank=True, null=True)),
                ('raw_health_requirements', models.TextField(blank=True, null=True)),
                ('raw_livelihoods_and_basic_needs_female', models.TextField(blank=True, null=True)),
                ('raw_livelihoods_and_basic_needs_male', models.TextField(blank=True, null=True)),
                ('raw_livelihoods_and_basic_needs_people_reached', models.TextField(blank=True, null=True)),
                ('raw_livelihoods_and_basic_needs_people_targeted', models.TextField(blank=True, null=True)),
                ('raw_livelihoods_and_basic_needs_requirements', models.TextField(blank=True, null=True)),
                ('raw_migration_female', models.TextField(blank=True, null=True)),
                ('raw_migration_male', models.TextField(blank=True, null=True)),
                ('raw_migration_people_reached', models.TextField(blank=True, null=True)),
                ('raw_migration_people_targeted', models.TextField(blank=True, null=True)),
                ('raw_migration_requirements', models.TextField(blank=True, null=True)),
                ('raw_protection_gender_and_inclusion_female', models.TextField(blank=True, null=True)),
                ('raw_protection_gender_and_inclusion_male', models.TextField(blank=True, null=True)),
                ('raw_protection_gender_and_inclusion_people_reached', models.TextField(blank=True, null=True)),
                ('raw_protection_gender_and_inclusion_people_targeted', models.TextField(blank=True, null=True)),
                ('raw_protection_gender_and_inclusion_requirements', models.TextField(blank=True, null=True)),
                ('raw_shelter_female', models.TextField(blank=True, null=True)),
                ('raw_shelter_male', models.TextField(blank=True, null=True)),
                ('raw_shelter_people_reached', models.TextField(blank=True, null=True)),
                ('raw_shelter_people_targeted', models.TextField(blank=True, null=True)),
                ('raw_shelter_requirements', models.TextField(blank=True, null=True)),
                ('raw_water_sanitation_and_hygiene_female', models.TextField(blank=True, null=True)),
                ('raw_water_sanitation_and_hygiene_male', models.TextField(blank=True, null=True)),
                ('raw_water_sanitation_and_hygiene_people_reached', models.TextField(blank=True, null=True)),
                ('raw_water_sanitation_and_hygiene_people_targeted', models.TextField(blank=True, null=True)),
                ('raw_water_sanitation_and_hygiene_requirements', models.TextField(blank=True, null=True)),
                ('raw_education_female', models.TextField(blank=True, null=True)),
                ('raw_education_male', models.TextField(blank=True, null=True)),
                ('raw_education_people_reached', models.TextField(blank=True, null=True)),
                ('raw_education_people_targeted', models.TextField(blank=True, null=True)),
                ('raw_education_requirements', models.TextField(blank=True, null=True)),
                ('file_name', models.TextField(blank=True, null=True)),
                ('appeal_launch_date', models.DateField(blank=True, null=True)),
                ('appeal_number', models.CharField(blank=True, max_length=20, null=True)),
                ('category_allocated', models.TextField(blank=True, null=True)),
                ('date_of_issue', models.DateField(blank=True, null=True)),
                ('dref_allocated', models.TextField(blank=True, null=True)),
                ('expected_end_date', models.DateField(blank=True, null=True)),
                ('expected_time_frame', models.TextField(blank=True, null=True)),
                ('glide_number', models.CharField(blank=True, max_length=18, null=True)),
                ('num_of_people_affected', models.IntegerField(blank=True, null=True)),
                ('num_of_people_to_be_assisted', models.IntegerField(blank=True, null=True)),
                ('disaster_risk_reduction_female', models.IntegerField(blank=True, null=True)),
                ('disaster_risk_reduction_male', models.IntegerField(blank=True, null=True)),
                ('disaster_risk_reduction_people_reached', models.IntegerField(blank=True, null=True)),
                ('disaster_risk_reduction_people_targeted', models.IntegerField(blank=True, null=True)),
                ('disaster_risk_reduction_requirements', models.IntegerField(blank=True, null=True)),
                ('health_female', models.IntegerField(blank=True, null=True)),
                ('health_male', models.IntegerField(blank=True, null=True)),
                ('health_people_reached', models.IntegerField(blank=True, null=True)),
                ('health_people_targeted', models.IntegerField(blank=True, null=True)),
                ('health_requirements', models.IntegerField(blank=True, null=True)),
                ('livelihoods_and_basic_needs_female', models.IntegerField(blank=True, null=True)),
                ('livelihoods_and_basic_needs_male', models.IntegerField(blank=True, null=True)),
                ('livelihoods_and_basic_needs_people_reached', models.IntegerField(blank=True, null=True)),
                ('livelihoods_and_basic_needs_people_targeted', models.IntegerField(blank=True, null=True)),
                ('livelihoods_and_basic_needs_requirements', models.IntegerField(blank=True, null=True)),
                ('migration_female', models.IntegerField(blank=True, null=True)),
                ('migration_male', models.IntegerField(blank=True, null=True)),
                ('migration_people_reached', models.IntegerField(blank=True, null=True)),
                ('migration_people_targeted', models.IntegerField(blank=True, null=True)),
                ('migration_requirements', models.IntegerField(blank=True, null=True)),
                ('protection_gender_and_inclusion_female', models.IntegerField(blank=True, null=True)),
                ('protection_gender_and_inclusion_male', models.IntegerField(blank=True, null=True)),
                ('protection_gender_and_inclusion_people_reached', models.IntegerField(blank=True, null=True)),
                ('protection_gender_and_inclusion_people_targeted', models.IntegerField(blank=True, null=True)),
                ('protection_gender_and_inclusion_requirements', models.IntegerField(blank=True, null=True)),
                ('shelter_female', models.IntegerField(blank=True, null=True)),
                ('shelter_male', models.IntegerField(blank=True, null=True)),
                ('shelter_people_reached', models.IntegerField(blank=True, null=True)),
                ('shelter_people_targeted', models.IntegerField(blank=True, null=True)),
                ('shelter_requirements', models.IntegerField(blank=True, null=True)),
                ('water_sanitation_and_hygiene_female', models.IntegerField(blank=True, null=True)),
                ('water_sanitation_and_hygiene_male', models.IntegerField(blank=True, null=True)),
                ('water_sanitation_and_hygiene_people_reached', models.IntegerField(blank=True, null=True)),
                ('water_sanitation_and_hygiene_people_targeted', models.IntegerField(blank=True, null=True)),
                ('water_sanitation_and_hygiene_requirements', models.IntegerField(blank=True, null=True)),
                ('education_female', models.IntegerField(blank=True, null=True)),
                ('education_male', models.IntegerField(blank=True, null=True)),
                ('education_people_reached', models.IntegerField(blank=True, null=True)),
                ('education_people_targeted', models.IntegerField(blank=True, null=True)),
                ('education_requirements', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]
