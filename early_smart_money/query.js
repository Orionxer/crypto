var myHeaders = new Headers();

myHeaders.append("x-api-key", "-3iYNcRok7Gm4EMl");

var requestOptions = {
	method: "GET",
	headers: myHeaders,
	redirect: "follow",
};

// 1. 定义基础 URL 和参数
const baseUrl = "https://api.shyft.to/sol/v1/transaction/history";
const params =  new URLSearchParams({
    network: "mainnet-beta",
    tx_num: "10",
    account: "ENfpbQUM5xAnNP8ecyEQGFJ6KwbuPjMwv7ZjR29cDuAb",
    enable_raw: "true",
	// before_tx_signature: "GF5tJVe6PZV2DFVhSYRZQSxisoH9YS8fTnGGwBqNcCYJ1jmyBr5VRVcKJRJRsK9TRsyrHmX7K1eEvqgPPvXxSBk",
	until_tx_signature: "2HsaCV28dDTQoGXdrcEm4bYKbc64GVB6Gd5iH3bbitdCuA6KWrfB8ynWtASdk9i49gx8cumGRySSQ76rksCWwSLH"
});

// 2. 拼接完整的请求 URL
const url = `${baseUrl}?${params.toString()}`;

fetch(url, requestOptions)
	.then(response => response.text())
	.then(result => console.log(result))
	.catch(error => console.log('error', error));
