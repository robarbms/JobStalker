import '../styles/api_service.css';

export default function ApiService () {
    return (
        <div className="api-service-notif">
            <p>Either the API service is not running or there is no content in the database yet.</p>
            <p>Make sure that the API service is running.</p>
            <p>Make sure that the scraper service is running.</p>
            <p>Once the API service is up and running and there is content available, it will show up here.</p>
        </div>
    )
}