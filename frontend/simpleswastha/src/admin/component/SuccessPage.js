export const SuccessPage = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
  
    useEffect(() => {
      const queryParams = new URLSearchParams(window.location.search);
      const bookingId = queryParams.get('booking_id');
  
      if (bookingId) {
        // You can fetch booking details here if needed
        setLoading(false);
      } else {
        setError('Invalid booking reference');
        setLoading(false);
      }
    }, []);
  
    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;
  
    return (
      <div className="success-page">
        <h1>Payment Successful!</h1>
        <p>Your appointment has been confirmed.</p>
        <button onClick={() => navigate('/appointments')}>
          View My Appointments
        </button>
      </div>
    );
  };