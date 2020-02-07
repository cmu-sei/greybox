# greybox specific shell settings:
[ -n "$SESSION_NAME" -a -n "$NODE_NAME" ] && {

  # set terminal mode:
  [ -n "$TERM" ] && export TERM=vt100

  # watch should expect first argument to also be an alias:
  alias watch='watch '

  # bitcoin client's default mode and config file:
  alias btcli='bitcoin-cli -regtest -conf=/etc/bitcoin/bitcoin.conf'

}
