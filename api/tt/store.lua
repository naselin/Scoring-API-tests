#!/usr/bin/tarantool
-- Tarantool init script

box.cfg {
  listen = 33013,
  background = true,
  log = '/var/log/store.log',
  pid_file = '/tmp/store.pid'
}

box.once("bootstrap", function()
    box.schema.user.grant('guest', 'read,write,execute', 'universe')
    local s = box.schema.space.create('interests')
    s:format({
    {name = 'id', type = 'unsigned'},
    {name = 'interest', type = 'string'},
    })
    s:create_index('primary', {
    type = 'hash',
    parts = {'id'}
    })
    s:insert{1, "cars"}
    s:insert{2, "pets"}
    s:insert{3, "travel"}
    s:insert{4, "hi-tech"}
    s:insert{5, "sport"}
    s:insert{6, "music"}
    s:insert{7, "books"}
    s:insert{8, "tv"}
    s:insert{9, "cinema"}
    s:insert{10, "geek"}
    s:insert{11, "otus"}
    s = box.schema.space.create('clients_interests')
    s:format({
    {name = 'client_id', type = 'unsigned'},
    {name = 'interest1_id', type = 'unsigned'},
    {name = 'interest2_id', type = 'unsigned'}
    })
    s:create_index('primary', {type = 'hash',parts = {'client_id'}})
    s:insert{1, 3, 7}
    s = box.schema.space.create('score')
    s:format({
    {name = 'uid', type = 'string'},
    {name = 'score', type = 'scalar'},
    {name = 'timestamp', type = 'unsigned'},
    {name = 'expired_period', type = 'unsigned'}
    })
    s:create_index('primary', {
    type = 'hash',
    parts = {'uid'}
    })
end)

function mysplit(inputstr, sep)
        if sep == nil then
                sep = "%s"
        end
        local t={}
        for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
                table.insert(t, str)
        end
        return t
end

function get_interests(req)
  local temp = mysplit(req, ':')
  local cid = tonumber(temp[2])
  if cid > 1000 then
    return nil
  else
    local int_list = box.space.clients_interests:select{cid}
    if int_list[1] ~= nil then
      local temp = int_list[1]
      local interest1 = box.space.interests:select{temp[2]}
      local tmp1 = interest1[1][2]
  	  local interest2 = box.space.interests:select{temp[3]}
      tmp2 = interest2[1][2]
      return box.tuple.new({tmp1, tmp2})
    else
      set_interests(cid)
	  return get_interests(req)
    end
  end
end

function set_interests(cid)
  local interest1 = math.random(1, 11)
  local interest2 = math.random(1, 11)
  local t = box.tuple.new({cid, interest1, interest2})
  box.space.clients_interests:insert(t)
end

function cache_set_score(req, score, ttl)
  local temp = mysplit(req, ':')
  local uid = temp[2]
  local ts = os.time()
  local t = box.tuple.new({uid, score, ts, ttl})
  box.space.score:replace(t)
end

function cache_get_score(req)
  local temp = mysplit(req, ':')
  local uid = temp[2]
  local scores = box.space.score:select{uid}
  if scores[1] ~= nil then
    local vals = scores[1]
    local score = vals[2]
    local timestamp = vals[3]
    local ttl = vals[4]
    if (os.time() - timestamp) > ttl then
      box.space.score:delete{uid}
      return nil
    else
      return score
    end
  else
    return nil
  end
end
