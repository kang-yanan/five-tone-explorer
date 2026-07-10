'use strict';
const cloudbase = require('@cloudbase/node-sdk');

exports.main = async (event) => {
  // CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  };

  // Handle preflight
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  try {
    const app = cloudbase.init({ env: 'five-tone-cathykang-d4b0676685c9' });
    const db = app.database();
    const body = typeof event.body === 'string' ? JSON.parse(event.body) : (event.body || event);
    const result = await db.collection('experiments').add(body);
    return { statusCode: 200, headers, body: JSON.stringify({ ok: true, id: result.id }) };
  } catch (e) {
    return { statusCode: 200, headers, body: JSON.stringify({ ok: false, error: e.message }) };
  }
};
