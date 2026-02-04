


export const AuthenticationPage = () => {
  return (
    <>
      <div className="bg-slate-50 min-h-screen p-4 md:p-8">
        <div className="max-w-3xl mx-auto space-y-8">
          
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold text-slate-900">API Authentication</h1>
            <p className="mt-2 text-lg text-slate-600">
              Our API uses Bearer Token authentication to secure endpoints.
            </p>
          </div>

          {/* Section 1: How to Authenticate */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-slate-900">How to Authenticate</h2>
            <p className="text-slate-600 leading-relaxed">
              You must include the <code className="bg-slate-200 px-1.5 py-0.5 rounded text-sm font-mono text-slate-800">Authorization</code> header with the format <code className="bg-slate-200 px-1.5 py-0.5 rounded text-sm font-mono text-slate-800">Bearer &lt;token&gt;</code> in all your requests to protected endpoints.
            </p>
          </section>

          {/* Section 2: Error Handling */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-slate-900">Error Handling</h2>
            
            {/* Info Alert Pattern */}
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r">
              <p className="font-bold text-blue-700">Note</p>
              <p className="text-sm text-blue-600">
                If the token is missing, expired, or invalid, the API returns a 401 Unauthorized status code.
              </p>
            </div>
          </section>

          {/* Section 3: Example Request */}
          <section className="space-y-4">
            <h2 className="text-2xl font-semibold text-slate-900">Example Request</h2>
            <p className="text-slate-600">
              Here is an example of how to make a request using cURL:
            </p>

            {/* Code Block Pattern */}
            <div className="bg-slate-900 text-white rounded-lg p-4 overflow-x-auto">
              <pre className="font-mono text-sm">
{`curl -X GET https://api.example.com/api/v1/products \\
  -H "Authorization: Bearer <your_access_token>"`}
              </pre>
            </div>
          </section>

        </div>
      </div>
    </>
  );
};
