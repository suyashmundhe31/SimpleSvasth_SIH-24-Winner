export const CancelPage = () => {
    const navigate = useNavigate();
  
    return (
      <div className="cancel-page">
        <h1>Payment Cancelled</h1>
        <p>Your appointment booking was not completed.</p>
        <button onClick={() => navigate(-1)}>
          Try Again
        </button>
      </div>
    );
  };