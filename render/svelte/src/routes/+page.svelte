<script lang="ts">
	import { onMount } from 'svelte';
	import './dashboard.scss';
	import type { DashboardInputData, Service, AirconData } from './models';
	import exampleData from './data.json';

	interface Train {
		time: string;
		destination: string;
		status: string;
		delay: string;
	}
	let currentTime: string, currentDay: string, currentDate: string;
	let northboundTrains: Train[] = [],
		southboundTrains: Train[] = [];
	let currentTemperature: string, minTemperature: string, maxTemperature: string;
	let weatherDescription: string;
	let airconData: AirconData[] = [];

	let airQualityIndex: number;
	const loadData = (data: DashboardInputData) => {
		const parsedTime = new Date(data.time);

		currentTime = parsedTime.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
		currentDay = parsedTime.toLocaleDateString('en-GB', { weekday: 'short' }).toUpperCase();
		currentDate = parsedTime
			.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
			.toUpperCase();

		northboundTrains =
			data.rail.northbound.trainServices?.service.map((service: Service) => ({
				time: service.std,
				destination: service.destination.location[0].locationName,
				status: service.etd,
				delay: getDelay(service, parsedTime)
			})) || [];

		southboundTrains =
			data.rail.southbound.trainServices?.service.map((service: Service) => ({
				time: service.std,
				destination: service.destination.location[0].locationName,
				status: service.etd,
				delay: getDelay(service, parsedTime)
			})) || [];

		currentTemperature = `${Math.round(data.weather.main.temp)}°C`;
		minTemperature = `${Math.round(data.weather.main.temp_min)}°C`;
		maxTemperature = `${Math.round(data.weather.main.temp_max)}°C`;
		weatherDescription = data.weather.weather[0].description;
		airQualityIndex = data.air_quality.list[0].main.aqi;
		airconData = data.aircon;
	};
	let loaded = false;
	const loadDataFromSource = (path: string) => {
		fetch(path)
			.then((response) => response.json() as Promise<DashboardInputData>)
			.then((data) => {
				loadData(data);
				loaded = true;
			})
			.catch((error) => console.error('Error:', error));
	};

	function getDelay(service: Service, now: Date): string {
		const arrivalTime = new Date(now.toISOString().split('T')[0] + 'T' + service.std + ':00');

		// If the arrival time is earlier than now, add one day
		if (arrivalTime < now) {
			arrivalTime.setDate(arrivalTime.getDate() + 1);
		}

		const delayInMinutes = Math.floor((arrivalTime.getTime() - now.getTime()) / 60000); // convert ms to mins
		const delayHours = Math.floor(delayInMinutes / 60);
		const delayMinutes = delayInMinutes % 60;

		if (delayInMinutes > 60) {
			return `${delayHours} HR ${delayMinutes} MINS`;
		} else {
			return `${delayInMinutes} MINS`;
		}
	}

	const useAPI = false; // Set this to true or false to choose between API and file loading

	onMount(async function () {
		if (useAPI) {
			const sourcePath = 'http://localhost:8000/get_dashboard_data';
			loadDataFromSource(sourcePath);
		} else {
			const dashboardData: DashboardInputData = exampleData;
			loadData(dashboardData);
		}
	});
</script>

<div class="container" class:loaded>
	<div class="time-date">
		<div class="time">{currentTime}</div>
		<div class="date">
			<div class="day">{currentDay}</div>
			<div class="date-num">{currentDate}</div>
		</div>
	</div>

	<table class="northbound">
		<thead>
			<tr>
				<th colspan="4">NORTHBOUND</th>
			</tr>
		</thead>
		<tbody>
			{#if northboundTrains.length === 0}
				<tr>
					<td colspan="4">No scheduled trains</td>
				</tr>
			{:else}
				{#each northboundTrains as train}
					<tr>
						<td>{train.time}</td>
						<td>{train.destination}</td>
						<td>{train.status}</td>
						<td>{train.delay}</td>
					</tr>
				{/each}
			{/if}
		</tbody>
	</table>

	<table class="southbound">
		<thead>
			<tr>
				<th colspan="4">SOUTHBOUND</th>
			</tr>
		</thead>
		<tbody>
			{#if southboundTrains.length === 0}
				<tr>
					<td colspan="4">No scheduled trains</td>
				</tr>
			{:else}
				{#each southboundTrains as train}
					<tr>
						<td>{train.time}</td>
						<td>{train.destination}</td>
						<td>{train.status}</td>
						<td>{train.delay}</td>
					</tr>
				{/each}
			{/if}
		</tbody>
	</table>

	<div class="weather">
		<div class="temperatures">
			<div class="current">{currentTemperature}</div>
			<div class="min-max">
				<div>{maxTemperature}</div>
				<div>{minTemperature}</div>
			</div>
		</div>
		<div class="additional-info">
			<div class="description">{weatherDescription}</div>
			<div class="AQI">AQI: {airQualityIndex}</div>
			<div class="aircon">
				{#each airconData as unit}
					<div>
						{unit.name}: {unit.temperature.indoor}C {unit.humidity}%
					</div>
				{/each}
				{#if airconData.length > 0}
					<div>
						Outdoor: {airconData[0].temperature.outdoor}C
					</div>
				{/if}
			</div>
		</div>
	</div>
</div>
