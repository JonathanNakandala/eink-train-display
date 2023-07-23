<script lang="ts">
	import { onMount } from 'svelte';
	import type {
		DashboardInputData,
		Service,
		AirconData,
		Train,
		RailwayInformation,
		WeatherData
	} from './models';
	import exampleData from './data.json';
	import './dashboard.scss';

	export let dashboardData: DashboardInputData;
	export let loaded = false;

	const useAPI = import.meta.env.VITE_USE_API !== 'false';
	let sourcePath = import.meta.env.VITE_DASHBOARD_URL;
	sourcePath = 'http://api:8000/get_dashboard_data';
	let currentTime: string, currentDay: string, currentDate: string;
	let northboundTrains: Train[] = [],
		southboundTrains: Train[] = [];
	let currentTemperature: string, minTemperature: string, maxTemperature: string;
	let weatherDescription: string;
	let airconData: AirconData[] = [];
	let airQualityIndex: number;

	let error = '';
	let loading = false;

	onMount(async () => {
		loading = true;
		if (useAPI) {
			try {
				console.log('Fetching Data from: ' + sourcePath);
				const res = await fetch(sourcePath);
				if (!res.ok) throw new Error('Failed to fetch');
				dashboardData = await res.json();
				loadData(dashboardData);
				loaded = true;
			} catch (err) {
				console.error(err);
				error = (err as Error).message;
			}
		} else {
			try {
				console.warn('Using example API data');
				dashboardData = exampleData;
				loadData(dashboardData);
				loaded = true;
			} catch (err) {
				console.error(err);
				error = (err as Error).message;
			}
		}
		loading = false;
	});
	function loadData(data: DashboardInputData) {
		parseTimeData(data.time);
		mapTrainData(data.rail);
		parseWeatherData(data.weather);
		airQualityIndex = data.air_quality.list[0].main.aqi;
		airconData = data.aircon;
	}

	function parseTimeData(timeData: string) {
		const parsedTime = new Date(timeData);
		currentTime = parsedTime.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
		currentDay = parsedTime.toLocaleDateString('en-GB', { weekday: 'short' }).toUpperCase();
		currentDate = parsedTime
			.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })
			.toUpperCase();
	}

	function mapTrainData(railData: RailwayInformation) {
		const { northbound, southbound } = railData;
		northboundTrains = mapTrains(northbound?.trainServices?.service || []);
		southboundTrains = mapTrains(southbound?.trainServices?.service || []);
	}

	function mapTrains(services: Service[]): Train[] {
		return services.map((service) => ({
			time: service.std,
			destination: service.destination.location[0].locationName,
			status: service.etd,
			delay: getDelay(service)
		}));
	}

	function parseWeatherData(weatherData: WeatherData) {
		currentTemperature = `${Math.round(weatherData.main.temp)}°C`;
		minTemperature = `${Math.round(weatherData.main.temp_min)}°C`;
		maxTemperature = `${Math.round(weatherData.main.temp_max)}°C`;
		weatherDescription = weatherData.weather[0].description;
	}

	function getDelay(service: Service): string {
		const now = new Date();
		const arrivalTime = new Date(now.toISOString().split('T')[0] + 'T' + service.std + ':00');

		if (arrivalTime <= now) {
			arrivalTime.setDate(arrivalTime.getDate() + 1);
		}

		const delayInMinutes = Math.floor((arrivalTime.getTime() - now.getTime()) / 60000);
		const delayHours = Math.floor(delayInMinutes / 60);
		const delayMinutes = delayInMinutes % 60;

		if (delayInMinutes > 60) {
			return `${delayHours} HR ${delayMinutes} MINS`;
		} else if (delayInMinutes > 0) {
			return `${delayInMinutes} MINS`;
		} else {
			return `ON TIME`;
		}
	}
</script>

<div class="container" class:loaded>
	{#if loading}
		<div>Loading...</div>
	{:else if error}
		<div>{error}</div>
	{:else if loaded}
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
	{:else}
		<div>Data has not been loaded</div>
	{/if}
</div>
