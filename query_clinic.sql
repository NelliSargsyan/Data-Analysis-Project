SELECT
	c.clinic_id,
	c.clinic_location,
	c.city,
	c.number_of_doctors,
	COUNT(a.appointment_id) AS total_appointments_booked,
	SUM(a.revenue_realized) AS gross_revenue,

	COUNT(DISTINCT a.patient_id) AS unique_patients_treated,
	SUM(p.chronic_condition_flag) AS total_cronic_cases,
	ROUND(AVG(p.age), 1) AS avg_patient_age,

	(c.monthly_fixed_cost + c.monthly_marketing_spend) AS total_operating_costs,

	(SUM(a.revenue_realized) - (c.monthly_fixed_cost + c.monthly_marketing_spend)) AS net_profit

FROM clinics c

LEFT JOIN appointments a ON c.clinic_id = a.clinic_id

LEFT JOIN patients p ON a.patient_id = p.patient_id

GROUP BY 
	c.clinic_id,
	c.clinic_location,
	c.city,
	c.number_of_doctors, 
	c.monthly_fixed_cost,
	c.monthly_marketing_spend



ORDER BY net_profit DESC



	
 	
	
	
	
	
