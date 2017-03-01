var bcoin = require('bcoin').set('main');

// SPV chains only store the chain headers.
var chain = new bcoin.chain({
  db: 'leveldb',
  location: process.env.HOME + '/spvchain',
  spv: true
});

var pool = new bcoin.pool({
  chain: chain,
  spv: true,
  maxPeers: 8
});

var walletdb = new bcoin.walletdb({ db: 'memory' });

pool.open().then(function() {
  return walletdb.open();
}).then(function() {
  return walletdb.create();
}).then(function(wallet) {
  console.log('Created wallet with address %s', wallet.getAddress('base58'));

  // Add our address to the spv filter.
  pool.watchAddress(wallet.getAddress());

  // Connect, start retrieving and relaying txs
  pool.connect();

  // Start the blockchain sync.
  var rid = setInterval( function(){
				if (pool.connected){
					console.log("Here we go!");
					pool.startSync();
					clearInterval(rid);
				} else {
					console.log("Waiting for pool...");
				}
			});

  pool.on('tx', function(tx) {
    wallet.addTX(tx);
  });
 
  pool.on('block', function(b) {
    console.log(b);
  });

  wallet.on('balance', function(balance) {
    console.log('Balance updated.');
    console.log(bcoin.amount.btc(balance.unconfirmed));
  });
});
