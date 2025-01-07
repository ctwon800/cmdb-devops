// import { request } from '@/api/service'

export const crudOptions = (vm) => {
  return {
    pageOptions: {
      compact: true
    },
    options: {
      height: '100%',
      rowId: 'id'
    },
    selectionRow: {
      align: 'center',
      width: 46
    },
    rowHandle: {
      width: 240,
      fixed: 'right',
      view: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Retrieve')
        }
      },
      edit: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Update')
        }
      },
      remove: {
        thin: true,
        text: '',
        disabled () {
          return !vm.hasPermissions('Delete')
        }
      }
    },
    viewOptions: {
      componentType: 'form'
    },
    formOptions: {
      defaultSpan: 12 // 默认的表单 span
    },
    indexRow: { // 或者直接传true,不显示title，不居中
      title: '序号',
      align: 'center',
      width: 60
    },
    columns: [
      {
        title: 'ID',
        key: 'id',
        disabled: true,
        form: {
          disabled: true
        }
      },
      {
        title: 'minute',
        key: 'minute',
        width: 145,
        dict: {
          data: vm.dictionary('minute')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'hour',
        key: 'hour',
        width: 145,
        dict: {
          data: vm.dictionary('hour')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'day_of_week',
        key: 'day_of_week',
        width: 145,
        dict: {
          data: vm.dictionary('day_of_week')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'day_of_month',
        key: 'day_of_month',
        width: 145,
        dict: {
          data: vm.dictionary('day_of_month')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      },
      {
        title: 'month_of_year',
        key: 'month_of_year',
        width: 145,
        dict: {
          data: vm.dictionary('month_of_year')
        },
        form: {
          show: false,
          component: {
            span: 12
          }
        }
      }
    ]
  }
}
